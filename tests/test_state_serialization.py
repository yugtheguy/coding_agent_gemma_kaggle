import tempfile
from pathlib import Path
from src.agent.state import AgentState, TaskState, Phase, SearchEvidence, FocusedSource, DependencyEvidence
from src.agent.state_serializer import to_dict, from_dict, snapshot_state, to_compact_context

def test_serialization_round_trip():
    state = AgentState()
    state.phase = Phase.LOCALIZE
    state.task = TaskState(task_id="T1", issue_text="fix")
    
    data = to_dict(state)
    state2 = from_dict(data)
    
    assert state2.phase == Phase.LOCALIZE
    assert state2.task.task_id == "T1"

def test_atomic_snapshot_write():
    state = AgentState()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "state.json"
        snapshot_state(state, str(p))
        assert p.exists()

def test_compact_context_deterministic():
    state = AgentState()
    state.task = TaskState(task_id="T1", issue_text="fix")
    for i in range(12):
        state.search_evidence.append(SearchEvidence(evidence_id=f"E{i}", source_type="TEXT", query="Q", summary="S"))
    
    ctx = to_compact_context(state)
    assert "TASK:" in ctx
    assert "T1" in ctx
    assert "fix" in ctx
    assert "... 2 additional items omitted" in ctx
