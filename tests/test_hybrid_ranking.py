from src.localization.hybrid_ranking import (
    run_hybrid_ranking, build_semantic_query, HybridLocalizationResult
)
from src.localization.localization_result import LocalizationResult, Confidence, FileCandidate, SymbolCandidate
from src.localization.query_expansion import QueryExpansion
from src.localization.semantic_backend import SemanticHit
from src.localization.anchors import SearchAnchors

def test_scenario_b_vocabulary_mismatch():
    lexical = LocalizationResult(
        query_anchors=SearchAnchors([]),
        file_candidates=[],
        symbol_candidates=[],
        search_backend="mock",
        stats={},
        confidence=Confidence.WEAK
    )
    
    qe = QueryExpansion(implementation_concepts=["cache", "invalidation"])
    
    hits = [
        SemanticHit("pkg/cache_manager.py", 0.9, 1),
        SemanticHit("pkg/configuration.py", 0.8, 2)
    ]
    
    hr = run_hybrid_ranking(lexical, hits, qe, "cache invalidation", 1)
    
    assert hr.semantic_used
    assert hr.semantic_usefulness == "USEFUL"
    assert len(hr.file_candidates) == 2
    assert hr.file_candidates[0].path == "pkg/cache_manager.py"
    assert hr.confidence == Confidence.WEAK

def test_scenario_c_semantic_supports_lexical():
    from src.localization.localization_result import FileType
    fc = FileCandidate("pkg/client.py", 45.0, 1, FileType.SOURCE, [], [])
    lexical = LocalizationResult(
        query_anchors=SearchAnchors([]),
        file_candidates=[fc],
        symbol_candidates=[],
        search_backend="mock",
        stats={},
        confidence=Confidence.MODERATE
    )
    qe = QueryExpansion(implementation_concepts=["client"])
    hits = [SemanticHit("pkg/client.py", 0.9, 1)]
    
    hr = run_hybrid_ranking(lexical, hits, qe, "client", 1)
    
    assert hr.file_candidates[0].path == "pkg/client.py"
    assert hr.file_candidates[0].score == 75.0 # 45 + 30
    assert hr.confidence == Confidence.MODERATE

def test_scenario_d_semantic_disagreement():
    from src.localization.localization_result import FileType
    sc = SymbolCandidate("ClientSession.close", "pkg/client.py", 1, 1, "k", 50.0, [], [])
    fc = FileCandidate("pkg/client.py", 50.0, 1, FileType.SOURCE, [], [])
    
    lexical = LocalizationResult(
        query_anchors=SearchAnchors([]),
        file_candidates=[fc],
        symbol_candidates=[sc],
        search_backend="mock",
        stats={},
        confidence=Confidence.MODERATE
    )
    
    qe = QueryExpansion(implementation_concepts=["session", "close"])
    hits = [SemanticHit("pkg/session_utils.py", 0.9, 1)]
    
    hr = run_hybrid_ranking(lexical, hits, qe, "session close", 1)
    
    assert hr.file_candidates[0].path == "pkg/client.py" # 50.0 > 30.0

def test_scenario_e_empty_semantic():
    lexical = LocalizationResult(
        query_anchors=SearchAnchors([]),
        file_candidates=[],
        symbol_candidates=[],
        search_backend="mock",
        stats={},
        confidence=Confidence.WEAK
    )
    
    qe = QueryExpansion(implementation_concepts=["cache"])
    
    hr = run_hybrid_ranking(lexical, [], qe, "cache", 1)
    
    assert hr.semantic_usefulness == "UNHELPFUL"
    assert hr.confidence == Confidence.WEAK
