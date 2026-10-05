import tempfile
from pathlib import Path
from src.localization.repository_view import RepositoryView

def test_repository_view_list_files():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        (root / "pkg").mkdir()
        (root / "pkg" / "foo.py").write_text("def x(): pass")
        (root / "tests").mkdir()
        (root / "tests" / "test_foo.py").write_text("def test_x(): pass")
        
        # ignore dirs
        (root / ".git").mkdir()
        (root / ".git" / "config").write_text("git config")
        
        # extensions
        (root / "pkg" / "ignore.so").write_text("binary")
        
        repo = RepositoryView(root)
        files = repo.list_candidate_files()
        
        rel_files = set(str(f.relative_to(root)).replace("\\", "/") for f in files)
        assert "pkg/foo.py" in rel_files
        assert "tests/test_foo.py" in rel_files
        assert ".git/config" not in rel_files
        assert "pkg/ignore.so" not in rel_files
