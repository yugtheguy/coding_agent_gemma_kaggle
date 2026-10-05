from src.localization.graph_policy import evaluate_graph_policy
from src.localization.hybrid_ranking import HybridLocalizationResult
from src.localization.localization_result import FileCandidate, SymbolCandidate, Confidence

def test_graph_policy_scenario_a():
    # DIRECT_CONTEXT_SUFFICIENT
    from src.localization.localization_result import FileType
    fc = FileCandidate("pkg/parser.py", 130.0, 1, FileType.SOURCE, [], [])
    sc = SymbolCandidate("pkg/parser.py::parse_value", "pkg/parser.py", 1, 1, "k", 60.0, [], [])
    hr = HybridLocalizationResult(
        query_anchors=None, file_candidates=[fc], symbol_candidates=[sc], search_backend="mock", stats={}, confidence=Confidence.STRONG
    )
    
    decision = evaluate_graph_policy(hr, 3)
    assert not decision.use_graph
    assert decision.reason == "DIRECT_CONTEXT_SUFFICIENT"
    
def test_graph_policy_seeds():
    fc = FileCandidate("pkg/parser.py", 100.0, 1, None, [], [])
    sc1 = SymbolCandidate("pkg/parser.py::parse_value", "pkg/parser.py", 1, 1, "k", 60.0, [], [])
    sc2 = SymbolCandidate("pkg/parser.py::parse_other", "pkg/parser.py", 1, 1, "k", 40.0, [], [])
    
    hr = HybridLocalizationResult(
        query_anchors=None, file_candidates=[fc], symbol_candidates=[sc1, sc2], search_backend="mock", stats={}, confidence=Confidence.MODERATE
    )
    
    decision = evaluate_graph_policy(hr, 3)
    assert decision.use_graph
    # seed 1 is >50, seed 2 is <50 but added because file is >100.
    assert len(decision.seeds) == 2
    assert "pkg/parser.py::parse_value" in decision.seeds
    assert "pkg/parser.py::parse_other" in decision.seeds
    
def test_graph_policy_budget():
    decision = evaluate_graph_policy(HybridLocalizationResult(None, [], [], "", {}, Confidence.MODERATE), 0)
    assert not decision.use_graph
    assert decision.reason == "GRAPH_BUDGET_EXHAUSTED"
