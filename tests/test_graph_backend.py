from src.localization.graph_backend import FakeGraphBackend, GraphNeighbor
from src.localization.graph_normalization import normalize_relation

def test_fake_graph_backend():
    mapping = {
        "pkg/client.py::ClientSession.close": {
            "CALLS": ["pkg/transport.py::close"],
            "CALLED_BY": ["pkg/session.py::shutdown"],
            "TESTED_BY": ["tests/test_client.py::test_double_close"]
        }
    }
    
    backend = FakeGraphBackend(mapping)
    
    neighbors = backend.get_neighbors("pkg/client.py::ClientSession.close")
    assert len(neighbors) == 3
    
    # Check normalized relation
    rel_map = {n.target: n.normalized_relation for n in neighbors}
    assert rel_map["pkg/transport.py::close"] == "CALLEE"
    assert rel_map["pkg/session.py::shutdown"] == "CALLER"
    assert rel_map["tests/test_client.py::test_double_close"] == "TEST_TARGET"
    
def test_normalize_relation():
    assert normalize_relation("CALLER") == "CALLER"
    assert normalize_relation("CALLED_BY") == "CALLER"
    assert normalize_relation("CALLS") == "CALLEE"
    assert normalize_relation("IMPORTS") == "IMPORT"
    assert normalize_relation("INHERITS_FROM") == "INHERITANCE"
    assert normalize_relation("OVERRIDES") == "OVERRIDE"
    assert normalize_relation("TESTED_BY") == "TEST_TARGET"
    assert normalize_relation("USES_THING") == "UNKNOWN"
