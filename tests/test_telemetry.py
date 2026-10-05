import tempfile
import json
from pathlib import Path
from src.infrastructure.telemetry import TelemetryLogger

def test_telemetry_append():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        logger = TelemetryLogger(p)
        logger.log_event("run1", "E1", {"a": 1})
        logger.log_event("run1", "E2", {"b": 2}, task_id="t1")
        
        lines = (p / "events.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        e1 = json.loads(lines[0])
        assert e1["event_type"] == "E1"
        assert "timestamp_utc" in e1
        e2 = json.loads(lines[1])
        assert e2["event_type"] == "E2"
        assert e2["task_id"] == "t1"
