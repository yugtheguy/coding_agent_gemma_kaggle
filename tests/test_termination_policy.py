from src.control.task_status import TaskStatus, Action
from src.control.termination_decision import TerminationDecision

def test_termination_decision():
    td = TerminationDecision(
        task_status=TaskStatus.SOLVED,
        action=Action.SUBMIT_CANDIDATE,
        reason="test",
        budget_state={},
        verification_state={},
        information_gain_state={},
        time_remaining=10.0,
        hard_limit_reached=False,
        soft_limit_reached=False,
        expected_next_value="HIGH",
        safe_to_submit=True,
        should_abandon=False
    )
    assert td.task_status == TaskStatus.SOLVED
