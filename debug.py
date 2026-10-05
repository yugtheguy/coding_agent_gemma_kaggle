from tests.test_e00_end_to_end import *
import logging
import subprocess
class L:
    def log_event(self, a, b, c, d=""): print(b, c)
backends = ControllerBackends(diagnosis_provider=MockDiagnosis(['READY']), patch_provider=MockPatch(), command_backend=MockCommand(['PASS']), submission_backend=FakeSubmissionBackend())
ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600), L())
res = ctrl.run(TaskInput('test1', 'issue', 'repo'), 'run1')
print(res)
print("Git diff:")
print(subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True).stdout)
print("Git status:")
print(subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout)
