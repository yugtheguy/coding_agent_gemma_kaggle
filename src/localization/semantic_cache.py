import hashlib
from typing import Dict, List, Optional
from .semantic_backend import SemanticHit

class SemanticCache:
    def __init__(self):
        self._cache = {}
        
    def _compute_key(self, query: str, k: int, repo_revision: str, config_hash: str) -> str:
        key_str = f"{query}|{k}|{repo_revision}|{config_hash}"
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()
        
    def get(self, query: str, k: int, repo_revision: str, config_hash: str) -> Optional[List[SemanticHit]]:
        key = self._compute_key(query, k, repo_revision, config_hash)
        return self._cache.get(key)
        
    def set(self, query: str, k: int, repo_revision: str, config_hash: str, hits: List[SemanticHit]):
        key = self._compute_key(query, k, repo_revision, config_hash)
        self._cache[key] = hits
