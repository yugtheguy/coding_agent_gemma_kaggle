import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class TelemetryLogger:
    def __init__(self, run_dir: Path):
        self.log_path = run_dir / "events.jsonl"
        self.run_dir = run_dir
        
    def log_event(self, run_id: str, event_type: str, payload: Dict[str, Any], task_id: Optional[str] = None):
        event = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_id,
            "event_type": event_type,
            "payload": payload
        }
        if task_id:
            event["task_id"] = task_id
            
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
            f.flush()
