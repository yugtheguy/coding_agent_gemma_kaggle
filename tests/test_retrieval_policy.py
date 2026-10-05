from src.agent.retrieval_policy import evaluate_retrieval_policy, RetrievalDecision
from src.localization.localization_result import LocalizationResult, Confidence, FileCandidate, SymbolCandidate

def test_policy_strong():
    lr = LocalizationResult(None, [], [], "", {}, Confidence.STRONG)
    dec = evaluate_retrieval_policy(lr, 1)
    assert not dec.use_semantic
    assert dec.reason == "LEXICAL_STRONG"

def test_policy_weak():
    lr = LocalizationResult(None, [], [], "", {}, Confidence.WEAK)
    dec = evaluate_retrieval_policy(lr, 1)
    assert dec.use_semantic
    assert dec.reason == "LEXICAL_WEAK"
    
def test_policy_budget_exhausted():
    lr = LocalizationResult(None, [], [], "", {}, Confidence.WEAK)
    dec = evaluate_retrieval_policy(lr, 0)
    assert not dec.use_semantic
    assert dec.reason == "SEMANTIC_BUDGET_EXHAUSTED"

def test_policy_moderate_ambiguity():
    fc1 = FileCandidate("f1", 45.0, 1, None, [], [])
    fc2 = FileCandidate("f2", 42.0, 2, None, [], [])
    
    # tied files
    lr = LocalizationResult(None, [fc1, fc2], [SymbolCandidate("a", "f1", 1, 1, "k", 10.0, [], [])], "", {}, Confidence.MODERATE)
    dec = evaluate_retrieval_policy(lr, 1)
    assert dec.use_semantic
    assert dec.reason == "LEXICAL_AMBIGUOUS_TIED_FILES"
    
    # no symbol
    fc1.score = 50.0
    lr2 = LocalizationResult(None, [fc1, fc2], [], "", {}, Confidence.MODERATE)
    dec2 = evaluate_retrieval_policy(lr2, 1)
    assert dec2.use_semantic
    assert dec2.reason == "LEXICAL_AMBIGUOUS_NO_SYMBOL"
