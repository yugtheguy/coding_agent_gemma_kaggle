import tempfile
import json
from pathlib import Path

from src.infrastructure.telemetry import TelemetryLogger
from src.control.task_status import TaskStatus, Action
from src.control.termination_decision import TerminationDecision

def test_stage_11_telemetry():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        logger = TelemetryLogger(root)
        
        dec = TerminationDecision(
            task_status=TaskStatus.STILL_INFORMATION_GAINING,
            action=Action.CONTINUE,
            reason="HIGH_VALUE_ACTION_REMAINS",
            budget_state={"model_turns": 10},
            verification_state={},
            information_gain_state={},
            time_remaining=100.0,
            hard_limit_reached=False,
            soft_limit_reached=False,
            expected_next_value="HIGH",
            safe_to_submit=False,
            should_abandon=False
        )
        
        logger.log_event("run1", "BUDGET_CHECK", {"model_turns": 10}, "task1")
        logger.log_event("run1", "TERMINATION_DECISION", {
            "task_status": dec.task_status.name,
            "action": dec.action.name,
            "reason": dec.reason
        }, "task1")
        
        events_file = root / "events.jsonl"
        events = [json.loads(line) for line in events_file.read_text().strip().split('\n')]
        event_types = [e["event_type"] for e in events]
        
        assert "BUDGET_CHECK" in event_types
        assert "TERMINATION_DECISION" in event_types

def test_stage_12_telemetry():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        logger = TelemetryLogger(root)
        
        logger.log_event("run1", "FINAL_CHECK_COMPLETED", {
            "status": "PASS",
            "patch_nonempty": True,
            "patch_hash": "abc"
        }, "task1")
        
        logger.log_event("run1", "PATCH_EXTRACTION_COMPLETED", {
            "status": "SUCCESS",
            "patch_bytes": 100
        }, "task1")
        
        events_file = root / "events.jsonl"
        events = [json.loads(line) for line in events_file.read_text().strip().split('\n')]
        event_types = [e["event_type"] for e in events]
        
        assert "FINAL_CHECK_COMPLETED" in event_types
        assert "PATCH_EXTRACTION_COMPLETED" in event_types
