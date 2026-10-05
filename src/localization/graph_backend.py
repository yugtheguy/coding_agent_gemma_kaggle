from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class GraphNeighbor:
    source: str
    target: str
    raw_relation: str
    normalized_relation: str
    path: Optional[str] = None
    symbol: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    backend_metadata: Optional[Dict[str, Any]] = None

@dataclass
class GraphSubgraph:
    nodes: List[str]
    edges: List[GraphNeighbor]

class GraphBackend:
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, max_neighbors: int = 50) -> List[GraphNeighbor]:
        raise NotImplementedError
        
    def get_subgraph(self, nodes: List[str]) -> GraphSubgraph:
        raise NotImplementedError

class FakeGraphBackend(GraphBackend):
    def __init__(self, mapping: Dict[str, Dict[str, List[str]]]):
        self.mapping = mapping
        self.call_count = 0
        
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, max_neighbors: int = 50) -> List[GraphNeighbor]:
        self.call_count += 1
        results = []
        if node in self.mapping:
            for rel, targets in self.mapping[node].items():
                if edge_type and rel != edge_type:
                    continue
                for t in targets:
                    path, sym = t.split("::") if "::" in t else (t, None)
                    from .graph_normalization import normalize_relation
                    results.append(GraphNeighbor(
                        source=node, target=t, raw_relation=rel, 
                        normalized_relation=normalize_relation(rel),
                        path=path, symbol=sym
                    ))
        return results[:max_neighbors]

class HarnessGraphBackend(GraphBackend):
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, max_neighbors: int = 50) -> List[GraphNeighbor]:
        raise RuntimeError("HarnessGraphBackend not bound to official Kaggle 'get_code_neighbors' tool.")
        
    def get_subgraph(self, nodes: List[str]) -> GraphSubgraph:
        raise RuntimeError("HarnessGraphBackend not bound to official Kaggle 'get_code_subgraph' tool.")
