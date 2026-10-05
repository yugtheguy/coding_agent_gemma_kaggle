from dataclasses import dataclass
from typing import List, Dict, Any
from .graph_backend import GraphNeighbor
from .localization_result import FocusedRead

@dataclass
class RankedDependency:
    neighbor: GraphNeighbor
    score: float
    rank: int
    supporting_seeds: List[str]
    supporting_relations: List[str]

@dataclass
class GraphExpansionResult:
    seeds: List[str]
    neighbors: List[GraphNeighbor]
    ranked_dependencies: List[RankedDependency]
    focused_reads: List[FocusedRead]
    stats: Dict[str, Any]
    confidence: str
    discovery_used: bool
    usefulness: str = "UNHELPFUL"

    def to_dependency_evidence(self) -> List[Any]:
        from src.agent.state import DependencyEvidence
        import time
        ev = []
        for i, rd in enumerate(self.ranked_dependencies):
            ev.append(DependencyEvidence(
                source=rd.neighbor.source,
                target=rd.neighbor.target,
                relation=rd.neighbor.normalized_relation,
                raw_relation=rd.neighbor.raw_relation,
                evidence_id=f"G{i+1:03d}"
            ))
        return ev
