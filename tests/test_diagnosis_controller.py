from src.agent.diagnosis_controller import DiagnosisController
from src.diagnosis.diagnosis_provider import MockDiagnosisProvider
from src.diagnosis.diagnosis_result import DiagnosisResult, RootCauseLocation
from src.diagnosis.action_selection import NextAction, ActionType, ActionCost
from src.agent.state import AgentState
from src.agent.state import SearchEvidence
from src.diagnosis.source_acquisition import SourceSnippet

def test_diagnosis_controller_success():
    res = DiagnosisResult(
        observation="obs",
        hypothesis_statement="hyp",
        supporting_evidence_ids=["E01"],
        disconfirming_evidence_ids=[],
        root_cause_location=RootCauseLocation("foo.py", "func", 1, 10),
        invariant="inv",
        confidence="HIGH",
        recommended_action=NextAction(ActionType.PATCH, ActionCost.CHEAP, "desc", "foo.py"),
        patch_readiness="READY"
    )
    provider = MockDiagnosisProvider(res)
    controller = DiagnosisController(provider)
    
    state = AgentState()
    state.budget.hard_model_turns = 5
    state.search_evidence = [SearchEvidence("E001", "LEXICAL", "query", confidence="STRONG")]
    
    status = controller.run_diagnosis(state, [SourceSnippet("foo.py", 1, 10, "content")])
    assert status == "SUCCESS"
    assert state.debug.active_hypothesis.statement == "hyp"
    assert state.debug.active_hypothesis.hypothesis_id == "H001"
    
def test_diagnosis_controller_contradiction():
    res1 = DiagnosisResult(
        observation="obs",
        hypothesis_statement="hyp1",
        supporting_evidence_ids=["E01"],
        disconfirming_evidence_ids=[],
        root_cause_location=None,
        invariant="inv",
        confidence="MEDIUM",
        recommended_action=NextAction(ActionType.RUN, ActionCost.MEDIUM, "desc"),
        patch_readiness="NEEDS_EVIDENCE"
    )
    provider = MockDiagnosisProvider(res1)
    controller = DiagnosisController(provider)
    
    state = AgentState()
    state.budget.hard_model_turns = 5
    state.search_evidence = [SearchEvidence("E001", "LEXICAL", "query", confidence="STRONG")]
    
    controller.run_diagnosis(state, [SourceSnippet("foo.py", 1, 10, "content")])
    assert state.debug.active_hypothesis.statement == "hyp1"
    
    res2 = DiagnosisResult(
        observation="obs2",
        hypothesis_statement="hyp2",
        supporting_evidence_ids=["E02"],
        disconfirming_evidence_ids=["E01"],
        root_cause_location=None,
        invariant="inv2",
        confidence="HIGH",
        recommended_action=NextAction(ActionType.PATCH, ActionCost.CHEAP, "desc"),
        patch_readiness="READY"
    )
    provider.mock_result = res2
    controller.run_diagnosis(state, [SourceSnippet("foo.py", 1, 10, "content")])
    
    assert state.debug.active_hypothesis.statement == "hyp2"
    assert state.debug.active_hypothesis.hypothesis_id == "H002"
    assert len(state.debug.rejected_hypotheses) == 1
    assert state.debug.rejected_hypotheses[0].statement == "hyp1"
