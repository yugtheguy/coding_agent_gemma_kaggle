import pytest
from src.agent.state import AgentState, Phase, TaskState, RequirementsState

def test_agent_state_creation():
    state = AgentState()
    assert state.phase == Phase.UNDERSTAND
    assert state.task is None

def test_task_preservation():
    state = AgentState()
    state.task = TaskState(task_id="T01", issue_text="Fix the bug")
    assert state.task.issue_text == "Fix the bug"

def test_requirements_storage():
    state = AgentState()
    state.requirements.must_do.append("preserve fragment")
    assert "preserve fragment" in state.requirements.must_do

def test_valid_phase_transition():
    state = AgentState()
    state.transition_to(Phase.LOCALIZE)
    assert state.phase == Phase.LOCALIZE

def test_invalid_phase_transition():
    state = AgentState()
    with pytest.raises(ValueError):
        state.transition_to(Phase.PATCH)

def test_backtracking_transition():
    state = AgentState(phase=Phase.VERIFY_TARGET)
    state.transition_to(Phase.PATCH)
    assert state.phase == Phase.PATCH
