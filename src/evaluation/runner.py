import os
import json
import time
from pathlib import Path
from dataclasses import asdict
from typing import List

from ..infrastructure.run_context import create_run_context, RunContext
from ..infrastructure.telemetry import TelemetryLogger
from ..infrastructure.io_utils import atomic_write_json
from ..infrastructure.progress import Progress
from ..infrastructure.cache import Cache
from .result_schema import TaskResult

class E00Runner:
    def __init__(self, repo_root: Path, config: dict, prompt_content: str, resume_run_id: str = None):
        self.repo_root = repo_root
        self.config = config
        
        runs_root = Path(os.environ.get("GEMMA_RUNS_ROOT", repo_root / "runs"))
        runs_root.mkdir(parents=True, exist_ok=True)
        
        cache_root = Path(os.environ.get("GEMMA_CACHE_ROOT", repo_root / "cache"))
        self.cache = Cache(cache_root)
        
        experiment_id = config.get("experiment_id", "E00")
        baseline_version = config.get("baseline_version", "v1")
        
        if resume_run_id:
            self.run_dir = runs_root / resume_run_id
            if not self.run_dir.exists():
                raise ValueError(f"Resume run dir {self.run_dir} not found")
            with open(self.run_dir / "metadata.json", "r") as f:
                old_metadata = json.load(f)
            new_ctx = create_run_context(experiment_id, baseline_version, config, prompt_content)
            if old_metadata.get("config_hash") != new_ctx.config_hash:
                raise ValueError(f"Config hash mismatch on resume: {old_metadata.get('config_hash')} != {new_ctx.config_hash}")
            self.ctx = RunContext(**old_metadata)
            self.is_resume = True
        else:
            self.ctx = create_run_context(experiment_id, baseline_version, config, prompt_content)
            self.run_dir = runs_root / self.ctx.run_id
            self.run_dir.mkdir(parents=True, exist_ok=True)
            atomic_write_json(self.run_dir / "metadata.json", asdict(self.ctx))
            self.is_resume = False
            
        (self.run_dir / "tasks").mkdir(exist_ok=True)
        self.telemetry = TelemetryLogger(self.run_dir)
        
    def _save_task_result(self, result: TaskResult):
        path = self.run_dir / "tasks" / f"{result.task_id}.json"
        atomic_write_json(path, asdict(result))

    def _generate_summary(self, results: List[TaskResult]):
        total = len(results)
        completed_this_invocation = sum(1 for r in results if r.status == "completed" and r.cache_status != "hit")
        skipped_completed = sum(1 for r in results if r.status == "completed" and r.cache_status == "hit")
        failed = sum(1 for r in results if r.status == "failed")
        skipped = sum(1 for r in results if r.status == "skipped")
        total_duration = sum(r.duration_seconds for r in results)
        
        summary = {
            "run_id": self.ctx.run_id,
            "experiment_id": self.ctx.experiment_id,
            "git_commit": self.ctx.git_commit,
            "config_hash": self.ctx.config_hash,
            "total_tasks": total,
            "completed_this_invocation": completed_this_invocation,
            "skipped_completed": skipped_completed,
            "failed": failed,
            "skipped": skipped,
            "total_duration": total_duration,
            "average_task_duration": total_duration / max(1, completed_this_invocation + failed),
            "cache_hits": sum(1 for r in results if r.cache_status == "hit"),
            "cache_misses": sum(1 for r in results if r.cache_status == "miss"),
        }
        atomic_write_json(self.run_dir / "summary.json", summary)

    def run(self, task_ids: List[str], dry_run: bool = False):
        self.telemetry.log_event(self.ctx.run_id, "RUN_STARTED", {"dry_run": dry_run, "task_count": len(task_ids)})
        progress = Progress(len(task_ids))
        
        results = []
        for task_id in task_ids:
            task_path = self.run_dir / "tasks" / f"{task_id}.json"
            if self.is_resume and task_path.exists():
                with open(task_path, "r") as f:
                    old_res = json.load(f)
                if old_res.get("status") == "completed":
                    print(f"[CACHE/RESULT HIT] — skipping task_id={task_id}")
                    progress.update(task_id, "skipped")
                    results.append(TaskResult(**old_res))
                    self.telemetry.log_event(self.ctx.run_id, "TASK_SKIPPED", {"reason": "completed_in_resume"}, task_id=task_id)
                    continue
                    
            self.telemetry.log_event(self.ctx.run_id, "TASK_STARTED", {}, task_id=task_id)
            start_t = time.time()
            
            # Cache check
            cache_meta = {"config_hash": self.ctx.config_hash}
            cached = self.cache.get("tasks", task_id)
            if cached and cached.get("metadata", {}).get("config_hash") == self.ctx.config_hash:
                self.telemetry.log_event(self.ctx.run_id, "CACHE_HIT", {"namespace": "tasks", "key": task_id}, task_id=task_id)
                status = "completed"
                cache_status = "hit"
            else:
                if cached:
                    self.telemetry.log_event(self.ctx.run_id, "CACHE_MISS", {"reason": "metadata_mismatch", "namespace": "tasks", "key": task_id}, task_id=task_id)
                else:
                    self.telemetry.log_event(self.ctx.run_id, "CACHE_MISS", {"reason": "not_found", "namespace": "tasks", "key": task_id}, task_id=task_id)
                status = "completed"
                cache_status = "miss"
                if not dry_run:
                    time.sleep(0.1) # fake work
                self.cache.set("tasks", task_id, {"status": "ok"}, cache_meta)
                self.telemetry.log_event(self.ctx.run_id, "CACHE_WRITE", {"namespace": "tasks", "key": task_id}, task_id=task_id)
                
            duration = int(time.time() - start_t)
            res = TaskResult(
                task_id=task_id,
                status=status,
                resolved=True,
                duration_seconds=duration,
                cache_status=cache_status,
                start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_t)),
                end_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )
            self._save_task_result(res)
            results.append(res)
            
            self.telemetry.log_event(self.ctx.run_id, "TASK_FINISHED", asdict(res), task_id=task_id)
            progress.update(task_id, status)
            
        self._generate_summary(results)
        self.telemetry.log_event(self.ctx.run_id, "RUN_FINISHED", {})
        return self.ctx.run_id
