import tempfile
from pathlib import Path
from src.localization.localization_result import FocusedRead
from src.diagnosis.source_acquisition import FakeSourceBackend, acquire_focused_source, merge_reads

def test_source_merge():
    reads = [
        FocusedRead("foo.py", 10, 50, "A"),
        FocusedRead("foo.py", 40, 80, "B"),
        FocusedRead("foo.py", 200, 240, "C"),
        FocusedRead("bar.py", 5, 10, "D")
    ]
    
    merged = merge_reads(reads)
    
    assert len(merged) == 3
    
    foo_merged = [r for r in merged if r.path == "foo.py" and r.line_start == 10]
    assert len(foo_merged) == 1
    assert foo_merged[0].line_end == 80
    assert "A" in foo_merged[0].reason
    assert "B" in foo_merged[0].reason
    
def test_source_limits():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "foo.py").write_text("\n".join(str(i) for i in range(1000)))
        (root / "bar.py").write_text("\n".join(str(i) for i in range(1000)))
        
        backend = FakeSourceBackend(root)
        
        reads = [
            FocusedRead("foo.py", 1, 150, "A"),  
            FocusedRead("bar.py", 1, 100, "B"),  
        ]
        
        snippets = acquire_focused_source(
            backend, reads, max_files=5, max_snippets=6, 
            max_lines_per_snippet=120, max_total_lines=200
        )
        
        assert len(snippets) == 2
        assert snippets[0].line_end == 120
        assert snippets[1].line_end == 80
        assert snippets[1].truncated == True
