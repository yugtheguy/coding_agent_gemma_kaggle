import tempfile
from pathlib import Path
from src.patching.patch_backend import LocalEditBackend, capture_snapshot

def test_edit_backend_success():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        backend = LocalEditBackend(root)
        backend.write_file("foo.py", "line1\nline2\nline3\n")
        
        snapshot = capture_snapshot(backend, "foo.py")
        assert snapshot.content == "line1\nline2\nline3\n"
        
        success = backend.edit_file("foo.py", "line2\n", "line2_modified\n")
        assert success
        
        content = backend.read_file("foo.py", 1, 10)
        assert "line2_modified" in content
        
def test_edit_backend_multiple():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        backend = LocalEditBackend(root)
        backend.write_file("foo.py", "line1\nline1\nline3\n")
        
        success = backend.edit_file("foo.py", "line1\n", "line2\n", allow_multiple=False)
        assert not success
        
def test_edit_backend_not_found():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        backend = LocalEditBackend(root)
        backend.write_file("foo.py", "line1\nline2\nline3\n")
        
        success = backend.edit_file("foo.py", "line4\n", "line5\n")
        assert not success
