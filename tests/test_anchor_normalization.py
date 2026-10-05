from src.localization.anchors import AnchorType
from src.localization.anchor_normalization import normalize_anchor

def test_normalize_file_path():
    assert normalize_anchor("src\\foo.py", AnchorType.FILE_PATH) == "src/foo.py"
    assert normalize_anchor("/workspace/pkg/foo.py", AnchorType.FILE_PATH) == "pkg/foo.py"

def test_normalize_config_key():
    assert normalize_anchor("--timeout", AnchorType.CONFIG_KEY) == "timeout"
    assert normalize_anchor("timeout", AnchorType.CONFIG_KEY) == "timeout"

def test_normalize_dotted_name():
    assert normalize_anchor("foo.bar()", AnchorType.DOTTED_NAME) == "foo.bar"
    assert normalize_anchor("foo.bar", AnchorType.DOTTED_NAME) == "foo.bar"

def test_normalize_backticked():
    assert normalize_anchor("foo.bar()", AnchorType.BACKTICKED_TERM) == "foo.bar"

def test_normalize_operation():
    assert normalize_anchor("percent-encodes", AnchorType.OPERATION) == "percent-encodes"

def test_normalize_domain_term():
    assert normalize_anchor("URL", AnchorType.DOMAIN_TERM) == "url"
