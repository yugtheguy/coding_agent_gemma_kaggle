from src.agent.retrieval_policy import evaluate_retrieval_policy
from src.localization.query_expansion import MockQueryExpansionProvider, QueryExpansion
from src.localization.semantic_backend import FakeSemanticBackend, SemanticHit
from src.localization.hybrid_ranking import build_semantic_query, run_hybrid_ranking
from src.localization.localization_result import LocalizationResult, Confidence
from src.localization.anchors import SearchAnchors

def test_semantic_localization_flow():
    # Scenario A: Strong lexical
    lexical_a = LocalizationResult(None, [], [], "", {}, Confidence.STRONG)
    dec_a = evaluate_retrieval_policy(lexical_a, 1)
    assert not dec_a.use_semantic
    
    # Scenario B: Weak lexical
    lexical_b = LocalizationResult(
        query_anchors=SearchAnchors([]),
        file_candidates=[],
        symbol_candidates=[],
        search_backend="mock",
        stats={},
        confidence=Confidence.WEAK
    )
    dec_b = evaluate_retrieval_policy(lexical_b, 1)
    assert dec_b.use_semantic
    
    provider = MockQueryExpansionProvider(QueryExpansion(implementation_concepts=["cache", "invalidation"]))
    expansion = provider.expand("issue text", "lexical summary")
    
    query = build_semantic_query(lexical_b, expansion)
    assert "cache" in query
    assert "invalidation" in query
    
    backend = FakeSemanticBackend({
        query: [SemanticHit("pkg/cache_manager.py", 0.9, 1)]
    })
    
    hits = backend.search(query, k=6)
    hr = run_hybrid_ranking(lexical_b, hits, expansion, query, 1)
    
    assert hr.semantic_used
    assert hr.file_candidates[0].path == "pkg/cache_manager.py"
    
def test_budget():
    dec = evaluate_retrieval_policy(LocalizationResult(None, [], [], "", {}, Confidence.WEAK), normal_calls_budget=0)
    assert not dec.use_semantic
