from src.patching.diff_inspection import inspect_diff, DiffInspectionResult
from src.patching.patch_backend import EditBackend

class MockBackend(EditBackend):
    def __init__(self, numstat, check=""):
        self.numstat = numstat
        self.check = check
        
    def run_command(self, command: str) -> str:
        if "numstat" in command:
            return self.numstat
        return self.check

def test_inspect_diff_clean():
    backend = MockBackend("10\t5\tfoo.py\n")
    res = inspect_diff(backend, "foo.py")
    assert res.scope == "CLEAN"
    assert res.files_changed == 1
    assert res.lines_added == 10
    assert res.lines_removed == 5
    
def test_inspect_diff_suspicious_files():
    backend = MockBackend("10\t5\tfoo.py\n2\t2\tbar.py\n")
    res = inspect_diff(backend, "foo.py")
    assert res.scope == "SUSPICIOUS"
    assert "bar.py" in res.unexpected_files
    
def test_inspect_diff_suspicious_size():
    backend = MockBackend("100\t50\tfoo.py\n")
    res = inspect_diff(backend, "foo.py", max_lines=100)
    assert res.scope == "SUSPICIOUS"
    
def test_inspect_diff_invalid():
    backend = MockBackend("")
    res = inspect_diff(backend, "foo.py")
    assert res.scope == "INVALID"
    assert not res.patch_nonempty
