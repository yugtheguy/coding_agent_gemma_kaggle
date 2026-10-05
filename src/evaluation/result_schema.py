from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskResult:
    task_id: str
    status: str
    resolved: bool = False
    patch_submitted: bool = False
    patch_nonempty: bool = False
    duration_seconds: int = 0
    model_turns: int = 0
    tool_calls: int = 0
    test_calls: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    start_time: str = ""
    end_time: str = ""
    cache_status: str = "miss"
