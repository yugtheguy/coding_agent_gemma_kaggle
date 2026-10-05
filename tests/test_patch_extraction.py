from src.submission.patch_extraction import extract_patch

def test_extract_patch():
    res = extract_patch(timeout_seconds=10)
    assert "status" in res
