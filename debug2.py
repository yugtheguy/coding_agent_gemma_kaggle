from tests.test_e00_end_to_end import *
import logging
class L:
    def log_event(self, a, b, c, d=""): print(b, c)
backends = ControllerBackends(diagnosis_provider=MockDiagnosis(['READY']), command_backend=MockCommand(['PASS']), submission_backend=FakeSubmissionBackend())
ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600), L())
res = ctrl.run(TaskInput('test1', 'issue', 'repo'), 'run1')
print(res)
