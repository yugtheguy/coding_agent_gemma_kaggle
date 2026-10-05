from src.localization.graph_backend import FakeGraphBackend
from src.localization.graph_policy import GraphDecision
from src.localization.graph_ranking import run_graph_expansion

def test_graph_ranking():
    mapping = {
        "seed_func": {
            "CALLS": ["callee_func"],
            "CALLED_BY": ["caller_func1", "caller_func2"],
            "IMPORTS": ["unrelated_import"]
        }
    }
    backend = FakeGraphBackend(mapping)
    decision = GraphDecision(True, ["seed_func"], [], "", 8, 20)
    
    result = run_graph_expansion(backend, decision)
    
    assert result.stats["graph_calls"] == 1
    assert result.stats["neighbors_returned"] == 4
    assert result.usefulness == "USEFUL"
    
    # Check ranking
    assert len(result.ranked_dependencies) == 4
    # caller > callee > import
    top_target = result.ranked_dependencies[0].neighbor.target
    assert top_target in ("caller_func1", "caller_func2")
    
def test_graph_hub_control():
    # 30 callers
    mapping = {
        "seed_func": {
            "CALLED_BY": [f"caller_{i}" for i in range(30)]
        }
    }
    backend = FakeGraphBackend(mapping)
    decision = GraphDecision(True, ["seed_func"], [], "", 8, 20)
    
    result = run_graph_expansion(backend, decision)
    
    assert result.stats["neighbors_returned"] == 30
    assert result.stats["neighbors_kept"] == 20
    assert len(result.ranked_dependencies) == 20
    assert result.usefulness == "MIXED" # >10 ranked items
    
def test_graph_multiple_seeds():
    mapping = {
        "seed1": {
            "CALLS": ["common_callee"]
        },
        "seed2": {
            "CALLS": ["common_callee"]
        }
    }
    backend = FakeGraphBackend(mapping)
    decision = GraphDecision(True, ["seed1", "seed2"], [], "", 8, 20)
    
    result = run_graph_expansion(backend, decision)
    
    assert result.stats["graph_calls"] == 2
    assert result.stats["neighbors_returned"] == 2
    assert result.stats["neighbors_kept"] == 1
    
    dep = result.ranked_dependencies[0]
    assert dep.neighbor.target == "common_callee"
    assert "seed1" in dep.supporting_seeds
    assert "seed2" in dep.supporting_seeds
