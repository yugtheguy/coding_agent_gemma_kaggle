import tempfile
from pathlib import Path
from src.localization.anchor_patterns import extract_anchors
from src.localization.ranking import run_localization
from src.localization.localization_result import Confidence

def setup_test_repo(root: Path):
    pkg = root / "pkg"
    pkg.mkdir()
    
    (pkg / "responses.py").write_text("""
class RedirectResponse:
    def __init__(self):
        self.headers = {"Location": ""}
        
    def encode(self, url_fragment):
        pass
""")
    
    (pkg / "utils.py").write_text("""
def parse_url(url):
    return url.fragment
""")

    (pkg / "client.py").write_text("""
class ClientSession:
    def close(self):
        raise ValueError('Session is already closed')
""")

    (pkg / "session_utils.py").write_text("""
def handle_session():
    pass
""")

    (pkg / "cache.py").write_text("""
def load_cache():
    pass
# cache cache cache cache cache cache cache cache
""")

    (pkg / "configuration.py").write_text("""
def reload_config():
    pass
""")

    (pkg / "reload.py").write_text("""
def reload():
    pass
""")

    (pkg / "unrelated.py").write_text("""
def unrelated():
    pass
""")

    tests = root / "tests"
    tests.mkdir()
    
    (tests / "test_responses.py").write_text("""
def test_redirect_fragment():
    location = "foo"
""")

def test_scenario_a_responses():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        setup_test_repo(root)
        
        issue = "`RedirectResponse` incorrectly percent-encodes URL fragments in pkg/responses.py when setting the `Location` header."
        anchors = extract_anchors(issue)
        result = run_localization(anchors, root)
        
        assert result.confidence == Confidence.STRONG
        assert result.file_candidates[0].path == "pkg/responses.py"
        assert result.symbol_candidates[0].qualified_name == "RedirectResponse"
        
        evidence = result.to_search_evidence()
        assert len(evidence) > 0
        assert evidence[0].source_type == "LOCALIZATION_FILE"
        assert "tests/test_responses.py" in [fc.path for fc in result.file_candidates]

def test_scenario_b_client_close():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        setup_test_repo(root)
        
        issue = "Calling ClientSession.close() twice raises ValueError: 'Session is already closed'."
        anchors = extract_anchors(issue)
        result = run_localization(anchors, root)
        
        assert result.file_candidates[0].path == "pkg/client.py"
        assert result.symbol_candidates[0].qualified_name == "ClientSession.close"

def test_scenario_c_weak_evidence():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        setup_test_repo(root)
        
        issue = "Cache entries are not invalidated after configuration reload."
        anchors = extract_anchors(issue)
        result = run_localization(anchors, root)
        
        assert result.confidence != Confidence.STRONG

def test_scenario_d_diversity():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        setup_test_repo(root)
        
        issue = "cache"
        anchors = extract_anchors(issue)
        result = run_localization(anchors, root)
        
        # Test just ensures it doesn't crash and we get some results
        assert len(result.file_candidates) > 0

def test_scenario_e_duplicate_filename():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        setup_test_repo(root)
        (root / "pkg" / "http").mkdir()
        (root / "pkg" / "http" / "responses.py").write_text("class HttpResponse: pass")
        
        issue = "pkg/http/responses.py"
        anchors = extract_anchors(issue)
        result = run_localization(anchors, root)
        
        assert result.file_candidates[0].path == "pkg/http/responses.py"
