from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SemanticHit:
    path: str
    score: float
    raw_rank: int
    symbol: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: Optional[str] = None
    backend_metadata: Optional[Dict] = None

class SemanticBackend:
    def search(self, query: str, k: int) -> List[SemanticHit]:
        raise NotImplementedError

class FakeSemanticBackend(SemanticBackend):
    def __init__(self, mapping: Dict[str, List[SemanticHit]]):
        self.mapping = mapping
        self.call_count = 0
        
    def search(self, query: str, k: int) -> List[SemanticHit]:
        self.call_count += 1
        results = self.mapping.get(query, [])
        return results[:k]

class HarnessSemanticBackend(SemanticBackend):
    def search(self, query: str, k: int) -> List[SemanticHit]:
        raise RuntimeError("HarnessSemanticBackend not bound to official Kaggle 'search_similar_code' tool.")
