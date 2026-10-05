from src.agent.state import AgentState, TaskState
from src.localization.localization_result import Confidence
from src.diagnosis.diagnosis_policy import evaluate_diagnosis_readiness

def test_diagnosis_policy_budget_exhausted():
    state = AgentState()
    state.budget.hard_model_turns = 0
    assert evaluate_diagnosis_readiness(state) == "BUDGET_EXHAUSTED"
    
def test_diagnosis_policy_weak_localization():
    state = AgentState()
    state.budget.hard_model_turns = 5
    from src.agent.state import SearchEvidence
    state.search_evidence = [SearchEvidence("E001", "LEXICAL", "query", confidence="WEAK")]
    assert evaluate_diagnosis_readiness(state) == "LOCALIZATION_TOO_WEAK"

def test_diagnosis_policy_need_source():
    state = AgentState()
    state.budget.hard_model_turns = 5
    from src.agent.state import SearchEvidence
    state.search_evidence = [SearchEvidence("E001", "LEXICAL", "query", confidence="STRONG")]
    state.focused_source = []
    assert evaluate_diagnosis_readiness(state) == "NEED_MORE_SOURCE"
