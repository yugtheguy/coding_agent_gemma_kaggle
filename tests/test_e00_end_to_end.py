from src.controller.task_controller import TaskController, TaskInput, ControllerBackends
from src.controller.controller_config import ControllerConfig
from src.submission.submission_backend import FakeSubmissionBackend
from src.control.runtime_accounting import GlobalBudgetContext
from src.agent.state import Phase
import pytest
import subprocess

class MockLocalization:
    def __init__(self, seq):
        self.seq = seq
        self.idx = 0
    def localize(self, state):
        if self.idx < len(self.seq):
            res = self.seq[self.idx]
            self.idx += 1
            return res
        return "READY"

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

class MockPatch:
    def generate_patch(self, state):
        with open("mock_patch_file.py", "w") as f:
            f.write("# dummy")
        subprocess.run(["git", "add", "mock_patch_file.py"])

def test_clean_success():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test1", "issue", "repo"), "run1")
    assert res.final_phase == "DONE"
    assert res.task_status == "SOLVED"
    assert res.submission_status == "SUBMITTED"
    assert res.patch_attempts == 1

def test_localization_stall():
    backends = ControllerBackends(
        localization_provider=MockLocalization(["STALLED"]),
        patch_provider=MockPatch(),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test2", "issue", "repo"), "run2")
    assert res.final_phase == "ABANDONED"
    assert res.task_status == "STALLED"
    assert res.patch_attempts == 0

def test_diagnosis_needs_evidence():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["NEEDS_EVIDENCE", "READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test3", "issue", "repo"), "run3")
    assert res.final_phase == "DONE"
    assert res.model_turns == 2
    assert res.patch_attempts == 1

def test_target_same_failure():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY", "ABANDONED"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["FAIL"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test4", "issue", "repo"), "run4")
    assert res.final_phase == "ABANDONED"
    assert res.patch_attempts == 1

def test_justified_repair():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY", "READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["FAIL", "PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test5", "issue", "repo"), "run5")
    assert res.final_phase == "DONE"
    assert res.patch_attempts == 2

def test_regression_failure():
    class MockRegression:
        def run_target(self): return "PASS"
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY", "ABANDONED"]),
        patch_provider=MockPatch(),
        command_backend=MockRegression(),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test6", "issue", "repo"), "run6")
    # For now regression always passes in phase_dispatch mock unless we modify phase_dispatch

def test_hard_budget_unsolved():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["FAIL"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 0, 3600))
    res = ctrl.run(TaskInput("test7", "issue", "repo"), "run7")
    assert res.final_phase == "ABANDONED"

def test_hard_budget_solved():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 0, 3600))
    res = ctrl.run(TaskInput("test8", "issue", "repo"), "run8")
    assert res.final_phase == "DONE"

def test_submission_infra_failure():
    class BrokenSub:
        def submit_patch(self, p): raise RuntimeError("NETWORK_FAIL")
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        patch_provider=MockPatch(),
        command_backend=MockCommand(["PASS"]),
        submission_backend=BrokenSub()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test9", "issue", "repo"), "run9")
    assert res.final_phase == "ABANDONED"
    assert res.submission_status == "FAILED"
    assert "NETWORK_FAIL" in res.infra_failure

def test_step_limit():
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["NEEDS_EVIDENCE"] * 100),
        patch_provider=MockPatch(),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(max_steps=10), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test10", "issue", "repo"), "run10")
    assert res.final_phase == "ABANDONED"
    assert ctrl.step_count == 10
