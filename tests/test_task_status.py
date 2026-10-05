from src.control.task_status import TaskStatus, Action

def test_task_status_enums():
    assert TaskStatus.SOLVED.value == "SOLVED"
    assert TaskStatus.STILL_INFORMATION_GAINING.value == "STILL_INFORMATION_GAINING"
    assert TaskStatus.STALLED.value == "STALLED"
    assert Action.CONTINUE.value == "CONTINUE"
    assert Action.SUBMIT_CANDIDATE.value == "SUBMIT_CANDIDATE"
    assert Action.ABANDON.value == "ABANDON"
