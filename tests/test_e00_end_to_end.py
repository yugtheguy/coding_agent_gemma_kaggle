from src.controller.task_controller import TaskController, TaskInput, ControllerBackends
from src.controller.controller_config import ControllerConfig
from src.submission.submission_backend import FakeSubmissionBackend
from src.control.runtime_accounting import GlobalBudgetContext

class MockDiagnosis:
    def __init__(self, sequence):
        self.seq = sequence
        self.idx = 0
    def diagnose(self, state):
        if self.idx < len(self.seq):
            res = self.seq[self.idx]
            self.idx += 1
            return res
        return "READY"

class MockCommand:
    def __init__(self, sequence):
        self.seq = sequence
        self.idx = 0
    def run_target(self):
        if self.idx < len(self.seq):
            res = self.seq[self.idx]
            self.idx += 1
            return res
        return "PASS"

def test_clean_success():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test1", "issue", "repo"), "run1")
    
    assert res.final_phase == "DONE"
    assert res.task_status == "SOLVED"
    assert res.submission_status == "SUBMITTED"

def test_diagnosis_needs_evidence():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["NEEDS_EVIDENCE", "READY"]),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test2", "issue", "repo"), "run2")
    
    assert res.final_phase == "DONE"
    assert res.model_turns == 2

def test_step_limit():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["NEEDS_EVIDENCE"] * 100),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(max_steps=10), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test3", "issue", "repo"), "run3")
    
    assert res.final_phase == "ABANDONED"
    assert ctrl.step_count == 10
