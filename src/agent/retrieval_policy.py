from dataclasses import dataclass
from typing import Optional
from src.localization.localization_result import Confidence as LexicalConfidence, LocalizationResult

@dataclass
class RetrievalDecision:
    use_query_expansion: bool
    use_semantic: bool
    reason: str
    semantic_calls_allowed: int

def evaluate_retrieval_policy(
    lexical_result: LocalizationResult, 
    normal_calls_budget: int = 1,
    recovery_triggered: bool = False
) -> RetrievalDecision:
    
    if normal_calls_budget <= 0:
        return RetrievalDecision(False, False, "SEMANTIC_BUDGET_EXHAUSTED", 0)

    if recovery_triggered:
        return RetrievalDecision(True, True, "RECOVERY_TRIGGERED", normal_calls_budget)

    conf = lexical_result.confidence
    
    if conf == LexicalConfidence.STRONG:
        return RetrievalDecision(False, False, "LEXICAL_STRONG", 0)
        
    if conf == LexicalConfidence.WEAK:
        return RetrievalDecision(True, True, "LEXICAL_WEAK", normal_calls_budget)
        
    # MODERATE
    files = lexical_result.file_candidates
    symbols = lexical_result.symbol_candidates
    
    if not symbols:
        return RetrievalDecision(True, True, "LEXICAL_AMBIGUOUS_NO_SYMBOL", normal_calls_budget)
        
    if len(files) >= 2:
        if (files[0].score - files[1].score) < 5.0:
            return RetrievalDecision(True, True, "LEXICAL_AMBIGUOUS_TIED_FILES", normal_calls_budget)
            
    return RetrievalDecision(False, False, "LEXICAL_MODERATE_UNAMBIGUOUS", 0)
