import tempfile
from pathlib import Path
import pytest
from src.evaluation.runner import E00Runner

def test_runner_resume():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        config = {"experiment_id": "TEST", "test": 1}
        
        import os
        os.environ["GEMMA_RUNS_ROOT"] = str(d / "runs")
        os.environ["GEMMA_CACHE_ROOT"] = str(d / "cache")
        
        runner1 = E00Runner(d, config, "prompt")
        run_id = runner1.run(["t1", "t2"], dry_run=True)
        
        runner2 = E00Runner(d, config, "prompt", resume_run_id=run_id)
        runner2.run(["t1", "t2", "t3"], dry_run=True)
        
        summary = (d / "runs" / run_id / "summary.json").read_text(encoding="utf-8")
        assert "3" in summary # 3 total tasks, completed/skipped appropriately
        
        with pytest.raises(ValueError, match="Config hash mismatch"):
            config["test"] = 2
            E00Runner(d, config, "prompt", resume_run_id=run_id)
