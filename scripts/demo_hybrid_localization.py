import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.localization.anchor_patterns import extract_anchors
from src.localization.ranking import run_localization
from src.agent.retrieval_policy import evaluate_retrieval_policy
from src.localization.query_expansion import MockQueryExpansionProvider, QueryExpansion
from src.localization.semantic_backend import FakeSemanticBackend, SemanticHit
from src.localization.hybrid_ranking import build_semantic_query, run_hybrid_ranking

def main():
    print("========================================")
    print("MOCK / INFRASTRUCTURE DEMO - STAGE 6")
    print("========================================\n")
    
    root = Path(__file__).resolve().parent.parent
    issue = "Cache entries are not invalidated after configuration reload."
    
    print(f"ISSUE:\n{issue}\n")
    
    print("1. Extracting Lexical Anchors...")
    anchors = extract_anchors(issue)
    lexical = run_localization(anchors, root)
    print(f"   Lexical Confidence: {lexical.confidence.name}")
    
    print("\n2. Evaluating Retrieval Policy...")
    decision = evaluate_retrieval_policy(lexical, normal_calls_budget=1)
    print(f"   Use Semantic: {decision.use_semantic} (Reason: {decision.reason})")
    
    if not decision.use_semantic:
        print("\nStopping at Lexical. No semantic search needed.")
        return
        
    print("\n3. Bounded Gemma Query Expansion (MOCK)...")
    provider = MockQueryExpansionProvider(QueryExpansion(
        implementation_concepts=["cache invalidation", "reload configuration", "stale cache"]
    ))
    expansion = provider.expand(issue, "")
    print(f"   Expanded concepts: {expansion.implementation_concepts}")
    
    query = build_semantic_query(lexical, expansion)
    print(f"   Semantic Query: '{query}'")
    
    print("\n4. Bounded Semantic Retrieval (FAKE BACKEND)...")
    backend = FakeSemanticBackend({
        query: [
            SemanticHit("src/agent/state.py", 0.85, 1),
            SemanticHit("experiments/E00.yaml", 0.75, 2)
        ]
    })
    
    hits = backend.search(query, k=6)
    print(f"   Returned {len(hits)} hits.")
    
    print("\n5. Hybrid Merging and Ranking...")
    hr = run_hybrid_ranking(lexical, hits, expansion, query, 1)
    
    print(f"   Semantic Usefulness: {hr.semantic_usefulness}")
    print(f"   Final Confidence: {hr.confidence.name}")
    print("\n   Top Files (Hybrid):")
    for fc in hr.file_candidates[:3]:
        print(f"   - {fc.path} (Score: {fc.score:.1f}, {fc.file_type.name})")

if __name__ == "__main__":
    main()
