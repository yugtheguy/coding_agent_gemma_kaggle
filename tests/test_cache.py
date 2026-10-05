import tempfile
from pathlib import Path
from src.infrastructure.cache import Cache
from src.infrastructure.io_utils import atomic_write_json

def test_atomic_write():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "test.json"
        atomic_write_json(p, {"a": 1})
        assert p.exists()

def test_cache_hit_miss():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        cache = Cache(p)
        assert cache.get("ns", "k1") is None
        cache.set("ns", "k1", "val", {"meta": 1})
        res = cache.get("ns", "k1")
        assert res["value"] == "val"
        assert res["metadata"] == {"meta": 1}
