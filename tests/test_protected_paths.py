from src.submission.protected_paths import is_protected, is_test_file

def test_is_protected():
    assert is_protected("agent.yaml")
    assert is_protected("experiments/config.yaml")
    assert is_protected(".github/workflows/main.yml")
    assert not is_protected("src/main.py")

def test_is_test_file():
    assert is_test_file("tests/test_main.py")
    assert is_test_file("test_utils.py")
    assert not is_test_file("src/utils.py")
