import tempfile
from pathlib import Path
from src.agent.state import AgentState, Phase, TaskState, SearchEvidence
from src.agent.debug_ledger import Hypothesis, NextAction
from src.agent.state_serializer import to_dict, from_dict, to_compact_context

def test_agent_state_full_demo():
    state = AgentState()
    
    state.task = TaskState(task_id="T1", issue_text="Fix the infinite loop.")
    
    assert state.phase == Phase.UNDERSTAND
    state.requirements.must_do.append("Stop the loop")
    
    state.transition_to(Phase.LOCALIZE)
    
    state.search_evidence.append(SearchEvidence(
        evidence_id="E001",
        source_type="LEXICAL",
        query="while True",
        path="src/main.py",
        summary="Found a potential infinite loop."
    ))
    
    state.transition_to(Phase.DIAGNOSE)
    
    h1 = Hypothesis(hypothesis_id="H001", statement="The loop condition never updates.", status="ACTIVE")
    state.update_hypothesis(h1)
    
    state.debug.active_hypothesis.supporting_evidence_ids.append("E001")
    
    state.debug.next_discriminating_action = NextAction(
        action_type="RUN",
        target="tests/test_main.py",
        reason="Verify loop behavior",
        expected_information="Timeout or crash",
        cost_class="MEDIUM"
    )
    
    state.debug.active_hypothesis.disconfirming_evidence_ids.append("E002")
    state.reject_hypothesis()
    
    h2 = Hypothesis(hypothesis_id="H002", statement="The loop breaks but is called infinitely.", status="ACTIVE")
    state.update_hypothesis(h2)
    
    data = to_dict(state)
    state2 = from_dict(data)
    
    assert state2.phase == Phase.DIAGNOSE
    assert state2.debug.active_hypothesis.hypothesis_id == "H002"
    assert len(state2.debug.rejected_hypotheses) == 1
    assert state2.debug.rejected_hypotheses[0].hypothesis_id == "H001"
    
    ctx = to_compact_context(state)
    assert "H002" in ctx
    assert "H001" not in ctx
