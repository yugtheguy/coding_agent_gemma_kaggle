from src.submission.artifact_cleanup import cleanup_agent_artifacts
import os

def test_cleanup_agent_artifacts():
    open("gemma_repro_test.py", "w").close()
    assert os.path.exists("gemma_repro_test.py")
    cleaned = cleanup_agent_artifacts(["gemma_repro_*.py"])
    assert cleaned == 1
    assert not os.path.exists("gemma_repro_test.py")
