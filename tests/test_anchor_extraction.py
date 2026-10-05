from src.localization.anchor_patterns import extract_anchors
from src.localization.anchors import AnchorType

def test_identifiers():
    text = "CamelCase snake_case UPPER_CASE __dunder__ foo.bar"
    anchors = extract_anchors(text).anchors
    types = [a.anchor_type for a in anchors]
    assert AnchorType.IDENTIFIER in types
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.IDENTIFIER]
    assert "CamelCase" in vals
    assert "snake_case" in vals
    assert "UPPER_CASE" in vals
    assert "__dunder__" in vals

def test_paths():
    text = "starlette/responses.py setup.cfg"
    anchors = extract_anchors(text).anchors
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.FILE_PATH]
    assert "starlette/responses.py" in vals
    assert "setup.cfg" in vals

def test_backticks():
    text = "`RedirectResponse`"
    anchors = extract_anchors(text).anchors
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.BACKTICKED_TERM]
    assert "RedirectResponse" in vals

def test_exception():
    text = "raises ValueError: 'invalid URL'"
    anchors = extract_anchors(text).anchors
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.EXCEPTION_NAME]
    assert "ValueError" in vals
    errs = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.ERROR_MESSAGE]
    assert "invalid URL" in errs

def test_assignment():
    text = "timeout=10 and --no-cache"
    anchors = extract_anchors(text).anchors
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.CONFIG_KEY]
    assert "timeout" in vals
    assert "no-cache" in vals

def test_noise_filtering():
    text = "The parser sometimes returns the wrong thing."
    anchors = extract_anchors(text).anchors
    vals = [a.normalized_value for a in anchors if a.anchor_type == AnchorType.IDENTIFIER]
    assert "The" not in vals
    assert "sometimes" not in vals
    assert "returns" not in vals

def test_search_plan():
    text = "`RedirectResponse` incorrectly percent-encodes URL fragment in starlette/responses.py when setting the `Location` header."
    anchors = extract_anchors(text)
    plan = anchors.to_search_plan()
    assert "PRIMARY EXACT:" in plan
    assert "RedirectResponse" in plan
    assert "Location" in plan
    assert "starlette/responses.py" in plan
    assert "CONCEPT TERMS:" in plan
    assert "url" in plan
    assert "fragment" in plan
