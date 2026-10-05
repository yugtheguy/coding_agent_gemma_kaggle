import os
import time
import json
import hashlib
import platform
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class RunContext:
    run_id: str
    experiment_id: str
    baseline_version: str
    start_time_utc: str
    git_commit: str
    git_branch: str
    working_tree_dirty: bool
    config_hash: str
    prompt_hash: str
    hostname: str
    python_version: str
    platform_info: str
    kaggle_detected: bool

def _run_cmd(cmd: list) -> str:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
    except Exception:
        return "unknown"

def create_run_context(experiment_id: str, baseline_version: str, config: dict, prompt_content: str) -> RunContext:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    git_commit = _run_cmd(["git", "rev-parse", "HEAD"])
    short_sha = git_commit[:7] if git_commit != "unknown" else "unknown"
    git_branch = _run_cmd(["git", "branch", "--show-current"])
    dirty_str = _run_cmd(["git", "status", "--porcelain"])
    dirty = bool(dirty_str) and dirty_str != "unknown"
    
    run_id = f"{experiment_id}_{timestamp}_{short_sha}"
    
    config_str = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()
    prompt_hash = hashlib.sha256((prompt_content or "").encode()).hexdigest()
    
    kaggle_detected = any(k in os.environ for k in ("KAGGLE_KERNEL_RUN_TYPE", "KAGGLE_URL_BASE")) or Path("/kaggle/working").exists()
    
    return RunContext(
        run_id=run_id,
        experiment_id=experiment_id,
        baseline_version=baseline_version,
        start_time_utc=timestamp,
        git_commit=git_commit,
        git_branch=git_branch,
        working_tree_dirty=dirty,
        config_hash=config_hash,
        prompt_hash=prompt_hash,
        hostname=platform.node(),
        python_version=platform.python_version(),
        platform_info=platform.platform(),
        kaggle_detected=kaggle_detected
    )
