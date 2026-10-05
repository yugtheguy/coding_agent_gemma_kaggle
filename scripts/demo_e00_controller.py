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

def main():
    print("========================================")
    print("MOCK E00 CONTROLLER DEMO")
    print("========================================")
    
    backends = ControllerBackends(
        diagnosis_provider=MockDiagnosis(["READY"]),
        command_backend=MockCommand(["PASS"]),
        submission_backend=FakeSubmissionBackend()
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("demo1", "fix bug", "repo"), "run_demo")
    
    print(f"Task Status: {res.task_status}")
    print(f"Final Phase: {res.final_phase}")
    print(f"Termination Reason: {res.termination_reason}")
    print(f"Submission Status: {res.submission_status}")
    print(f"Model Turns: {res.model_turns}")
    print(f"Tool Calls: {res.tool_calls}")

if __name__ == "__main__":
    main()
