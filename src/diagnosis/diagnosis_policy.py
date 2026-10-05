from src.agent.state import AgentState

def evaluate_diagnosis_readiness(state: AgentState) -> str:
    if state.budget.hard_model_turns <= 0:
        return "BUDGET_EXHAUSTED"
        
    has_strong = any(e.confidence == "STRONG" for e in state.search_evidence)
    has_moderate = any(e.confidence == "MODERATE" for e in state.search_evidence)
    
    if not has_strong and not has_moderate:
        return "LOCALIZATION_TOO_WEAK"
        
    if not state.focused_source:
        return "NEED_MORE_SOURCE"
        
    return "READY_FOR_DIAGNOSIS"
