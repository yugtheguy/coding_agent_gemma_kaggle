import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from .io_utils import atomic_write_json

class Cache:
    def __init__(self, cache_root: Path):
        self.cache_root = cache_root
        self.cache_root.mkdir(parents=True, exist_ok=True)
        
    def _get_path(self, namespace: str, key: str) -> Path:
        return self.cache_root / namespace / f"{key}.json"
        
    def get(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        path = self._get_path(namespace, key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
            
    def set(self, namespace: str, key: str, value: Any, metadata: Dict[str, Any]):
        path = self._get_path(namespace, key)
        data = {
            "value": value,
            "metadata": metadata,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        atomic_write_json(path, data)
