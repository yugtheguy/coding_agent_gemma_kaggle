import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.localization.graph_backend import FakeGraphBackend
from src.localization.graph_policy import GraphDecision
from src.localization.graph_ranking import run_graph_expansion

def main():
    print("========================================")
    print("MOCK GRAPH DEMO - STAGE 7")
    print("========================================\n")
    
    mapping = {
        "pkg/client.py::Client.close": {
            "CALLS": ["pkg/transport.py::close"],
            "CALLED_BY": ["pkg/session.py::shutdown", "pkg/app.py::cleanup"],
            "IMPORTS": ["pkg/utils.py"],
            "TESTED_BY": ["tests/test_client.py::test_close_twice"]
        }
    }
    
    backend = FakeGraphBackend(mapping)
    decision = GraphDecision(
        use_graph=True,
        seeds=["pkg/client.py::Client.close"],
        requested_relations=["CALLER", "CALLEE", "INHERITANCE", "OVERRIDE", "IMPORT", "TEST_TARGET", "REFERENCE"],
        reason="DEPENDENCY_UNCERTAINTY",
        max_neighbors_per_seed=8,
        total_neighbor_budget=20
    )
    
    print(f"SEED:\n{decision.seeds[0]}\n")
    print(f"Graph Decision:\n{decision.use_graph} (Reason: {decision.reason})\n")
    print(f"Relations Requested:\n{decision.requested_relations}\n")
    
    hr = run_graph_expansion(backend, decision)
    
    print(f"Neighbors Returned: {hr.stats['neighbors_returned']}")
    print(f"Neighbors Retained: {hr.stats['neighbors_kept']}\n")
    
    print("Ranked Dependencies:")
    for dep in hr.ranked_dependencies:
        print(f"  [{dep.rank}] {dep.neighbor.target} (Score: {dep.score:.1f}, Relation: {dep.neighbor.normalized_relation})")
        
    print("\nFocused Reads:")
    for r in hr.focused_reads:
        print(f"  - {r.path}:{r.line_start}-{r.line_end} ({r.reason})")
        
    print(f"\nGraph Calls Used: {hr.stats['graph_calls']}")

if __name__ == "__main__":
    main()
