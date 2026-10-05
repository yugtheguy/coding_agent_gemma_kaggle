from src.localization.semantic_cache import SemanticCache
from src.localization.semantic_backend import SemanticHit

def test_semantic_cache():
    cache = SemanticCache()
    hits = [SemanticHit("pkg/cache_manager.py", 0.9, 1)]
    
    # MISS
    assert cache.get("cache", 6, "rev1", "config1") is None
    
    # SET
    cache.set("cache", 6, "rev1", "config1", hits)
    
    # HIT
    assert cache.get("cache", 6, "rev1", "config1") == hits
    
    # MISS (diff query)
    assert cache.get("cache_different", 6, "rev1", "config1") is None
    
    # MISS (diff revision)
    assert cache.get("cache", 6, "rev2", "config1") is None
    
    # MISS (diff k)
    assert cache.get("cache", 12, "rev1", "config1") is None
