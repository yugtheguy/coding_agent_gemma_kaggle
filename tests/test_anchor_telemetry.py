import json
import tempfile
from pathlib import Path
from src.localization.anchor_patterns import extract_anchors
from src.infrastructure.telemetry import TelemetryLogger

def test_anchors_extracted_telemetry():
    with tempfile.TemporaryDirectory() as td:
        logger = TelemetryLogger(Path(td))
        run_id = "test_run_1"
        task_id = "task_1"
        
        text = "`RedirectResponse` incorrectly percent-encodes URL fragments in starlette/responses.py when setting the `Location` header."
        extract_anchors(text, telemetry_logger=logger, run_id=run_id, task_id=task_id)
        
        events_file = Path(td) / "events.jsonl"
        assert events_file.exists()
        
        lines = events_file.read_text().strip().split('\n')
        assert len(lines) == 1
        
        event = json.loads(lines[0])
        assert event["event_type"] == "ANCHORS_EXTRACTED"
        assert event["payload"]["path_count"] == 1
        assert "RedirectResponse" in event["payload"]["top_anchors"]
        assert "starlette/responses.py" in event["payload"]["top_anchors"]
