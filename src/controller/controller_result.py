from dataclasses import dataclass
from typing import Optional

@dataclass
class ControllerResult:
    task_id: str
    final_phase: str
    task_status: str
    submission_status: str
    termination_reason: str
    patch_hash: str
    resolved_locally: bool
    infra_failure: Optional[str]
    elapsed_seconds: float
    model_turns: int
    tool_calls: int
    semantic_calls: int
    graph_calls: int
    patch_attempts: int
    trajectory_event_count: int
