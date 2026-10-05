from src.diagnosis.execution_evidence import extract_salient_output, extract_traceback_signal

def test_extract_traceback():
    out = """Running tests...
Traceback (most recent call last):
  File "foo.py", line 10, in <module>
    raise ValueError("bad token")
ValueError: bad token
"""
    tb = extract_traceback_signal(out)
    assert "ValueError: bad token" in tb
    assert "File \"foo.py\"" in tb
    
def test_extract_salient():
    lines = [f"Line {i}" for i in range(100)]
    lines.insert(50, "=================================== FAILURES ===================================")
    for i in range(5):
        lines.insert(51+i, f"Failure info {i}")
    lines.insert(56, "=========================== short test summary info ===========================")
    
    out = "\n".join(lines)
    sal = extract_salient_output(out)
    
    assert "Line 0" in sal
    assert "... [truncated] ..." in sal
    assert "Failure info 0" in sal
    assert "Line 99" in sal
