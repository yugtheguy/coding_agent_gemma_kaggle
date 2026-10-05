import tempfile
import json
from pathlib import Path

from src.infrastructure.telemetry import TelemetryLogger
from src.agent.retrieval_policy import evaluate_retrieval_policy
from src.localization.query_expansion import MockQueryExpansionProvider, QueryExpansion
from src.localization.semantic_backend import FakeSemanticBackend, SemanticHit
from src.localization.hybrid_ranking import build_semantic_query, run_hybrid_ranking
from src.localization.localization_result import LocalizationResult, Confidence
from src.localization.anchors import SearchAnchors

def test_telemetry_emission_stage_6():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        logger = TelemetryLogger(root)
        
        lexical_b = LocalizationResult(
            query_anchors=SearchAnchors([]),
            file_candidates=[],
            symbol_candidates=[],
            search_backend="mock",
            stats={},
            confidence=Confidence.WEAK
        )
        
        provider = MockQueryExpansionProvider(QueryExpansion(implementation_concepts=["cache", "invalidation"]))
        expansion = provider.expand("issue text", "lexical summary")
        logger.log_event("run1", "QUERY_EXPANSION_COMPLETED", {
            "implementation_concept_count": len(expansion.implementation_concepts),
            "test_term_count": len(expansion.test_terms),
            "alternative_symbol_count": len(expansion.alternative_symbols),
            "truncated": expansion.truncated,
            "duration_ms": 10.0
        }, "task1")
        
        query = build_semantic_query(lexical_b, expansion)
        
        backend = FakeSemanticBackend({
            query: [SemanticHit("pkg/cache_manager.py", 0.9, 1)]
        })
        hits = backend.search(query, k=6)
        
        logger.log_event("run1", "SEMANTIC_SEARCH_COMPLETED", {
            "query": query,
            "k": 6,
            "result_count": len(hits),
            "unique_files": 1,
            "usefulness": "USEFUL",
            "semantic_call_number": 1,
            "duration_ms": 15.0
        }, "task1")
        
        hr = run_hybrid_ranking(lexical_b, hits, expansion, query, 1, telemetry_logger=logger, run_id="run1", task_id="task1")
        
        events_file = root / "events.jsonl"
        assert events_file.exists()
        
        events = [json.loads(line) for line in events_file.read_text().strip().split('\n')]
        event_types = [e["event_type"] for e in events]
        
        assert "QUERY_EXPANSION_COMPLETED" in event_types
        assert "SEMANTIC_SEARCH_COMPLETED" in event_types
        assert "HYBRID_LOCALIZATION_COMPLETED" in event_types
