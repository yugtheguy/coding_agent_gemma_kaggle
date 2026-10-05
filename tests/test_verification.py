from src.patching.verification import classify_target_failure, run_syntax_check
from src.patching.patch_backend import EditBackend

class MockBackend(EditBackend):
    def __init__(self, out):
        self.out = out
    def run_command(self, command: str) -> str:
        return self.out

def test_run_syntax_check():
    backend = MockBackend("")
    assert run_syntax_check(backend, "foo.py")
    
    backend = MockBackend("  File \"foo.py\", line 1\n    return 1  ++\nSyntaxError: invalid syntax")
    assert not run_syntax_check(backend, "foo.py")
    
def test_classify_target_failure():
    assert classify_target_failure(False, True, True, False) == "SYNTAX_FAILED"
    assert classify_target_failure(False, False, False, True) == "INFRA/ENVIRONMENT"
    assert classify_target_failure(False, True, False, False) == "TARGET_TIMEOUT"
    assert classify_target_failure(True, False, False, False) == "TARGET_FAILED_SAME_REASON"
    assert classify_target_failure(False, False, False, False) == "TARGET_FAILED_NEW_REASON"
