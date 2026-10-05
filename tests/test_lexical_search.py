import tempfile
from pathlib import Path
from src.localization.lexical import search_text

def test_python_fallback_search():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        (root / "pkg").mkdir()
        f = root / "pkg" / "foo.py"
        f.write_text("def parse_url():\n    return 42\n")
        
        hits = search_text("parse_url", root, backend="python")
        assert len(hits) == 1
        assert hits[0]["path"] == "pkg/foo.py"
        assert hits[0]["line"] == 1
        
        hits_case = search_text("PARSE_URL", root, ignore_case=True, backend="python")
        assert len(hits_case) == 1
