import time
from typing import List, Dict

from .graph_backend import GraphBackend, GraphNeighbor
from .graph_policy import GraphDecision
from .graph_result import GraphExpansionResult, RankedDependency
from .localization_result import FocusedRead

RELATION_WEIGHTS = {
    "CALLER": 10.0,
    "REFERENCE": 9.0,
    "CALLEE": 8.0,
    "INHERITANCE": 7.0,
    "OVERRIDE": 7.0,
    "IMPORT": 4.0,
    "TEST_TARGET": 5.0,
    "UNKNOWN": 1.0
}

def run_graph_expansion(
    backend: GraphBackend,
    decision: GraphDecision,
    telemetry_logger=None,
    run_id: str="",
    task_id: str=""
) -> GraphExpansionResult:
    start_time = time.time()
    
    all_neighbors = []
    stats = {
        "graph_calls": 0,
        "seeds_expanded": len(decision.seeds),
        "neighbors_returned": 0,
        "unknown_relations": 0,
        "relations_seen": []
    }
    
    for seed in decision.seeds:
        try:
            neighbors = backend.get_neighbors(seed, max_neighbors=decision.max_neighbors_per_seed) 
            stats["graph_calls"] += 1
            all_neighbors.extend(neighbors)
        except Exception:
            continue
            
    stats["neighbors_returned"] = len(all_neighbors)
    
    dep_map = {} 
    for n in all_neighbors:
        rel = n.normalized_relation
        if rel not in stats["relations_seen"]:
            stats["relations_seen"].append(rel)
        if rel == "UNKNOWN":
            stats["unknown_relations"] += 1
            
        key = n.target
        if key not in dep_map:
            dep_map[key] = RankedDependency(
                neighbor=n,
                score=0.0,
                rank=0,
                supporting_seeds=[],
                supporting_relations=[]
            )
            
        rd = dep_map[key]
        if n.source not in rd.supporting_seeds:
            rd.supporting_seeds.append(n.source)
        if n.raw_relation not in rd.supporting_relations:
            rd.supporting_relations.append(n.raw_relation)
            
        rd.score += RELATION_WEIGHTS.get(rel, 1.0)
        
    ranked = list(dep_map.values())
    
    ranked.sort(key=lambda x: (-x.score, x.neighbor.target))
    ranked = ranked[:decision.total_neighbor_budget]
    
    for i, rd in enumerate(ranked):
        rd.rank = i + 1
        
    # SUBGRAPH (Optional)
    if len(ranked) >= 2:
        top_nodes = [rd.neighbor.target for rd in ranked[:6]]
        try:
            subgraph = backend.get_subgraph(top_nodes)
            stats["graph_calls"] += 1
            # We integrate subgraph edges if any
            for edge in subgraph.edges:
                if edge.normalized_relation not in stats["relations_seen"]:
                    stats["relations_seen"].append(edge.normalized_relation)
        except Exception:
            pass

    usefulness = "UNHELPFUL"
    if ranked:
        useful_rels = sum(1 for rd in ranked if rd.neighbor.normalized_relation in ("CALLER", "CALLEE", "INHERITANCE", "TEST_TARGET", "OVERRIDE"))
        if useful_rels > 0:
            if len(ranked) > 10:
                usefulness = "MIXED"
            else:
                usefulness = "USEFUL"
                
    focused_reads = []
    for rd in ranked[:3]:
        n = rd.neighbor
        if n.path:
            start = n.line_start or 1
            end = n.line_end or (start + 15)
            reason = f"Graph dependency ({n.normalized_relation}) from {n.source}"
            focused_reads.append(FocusedRead(n.path, max(1, start - 5), end + 5, reason))
            
    stats["neighbors_kept"] = len(ranked)
    stats["duration_ms"] = (time.time() - start_time) * 1000
    
    result = GraphExpansionResult(
        seeds=decision.seeds,
        neighbors=all_neighbors,
        ranked_dependencies=ranked,
        focused_reads=focused_reads,
        stats=stats,
        confidence="STRONG" if usefulness == "USEFUL" else "WEAK",
        discovery_used=False,
        usefulness=usefulness
    )
    
    if telemetry_logger and run_id:
        telemetry_logger.log_event(run_id, "GRAPH_DECISION", {
            "use_graph": decision.use_graph,
            "reason": decision.reason,
            "seeds": decision.seeds
        }, task_id)
        
        telemetry_logger.log_event(run_id, "GRAPH_EXPANSION_COMPLETED", {
            "seeds": stats["seeds_expanded"],
            "graph_calls": stats["graph_calls"],
            "neighbors_returned": stats["neighbors_returned"],
            "neighbors_kept": stats["neighbors_kept"],
            "relations_seen": stats["relations_seen"],
            "unknown_relation_count": stats["unknown_relations"],
            "usefulness": usefulness,
            "duration_ms": stats["duration_ms"]
        }, task_id)
        
    return result
