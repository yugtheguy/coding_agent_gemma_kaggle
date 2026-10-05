from dataclasses import dataclass
from typing import Dict, Any
from src.control.task_status import TaskStatus, Action

@dataclass
class TerminationDecision:
    task_status: TaskStatus
    action: Action
    reason: str
    budget_state: Dict[str, Any]
    verification_state: Dict[str, Any]
    information_gain_state: Dict[str, Any]
    time_remaining: float
    hard_limit_reached: bool
    soft_limit_reached: bool
    expected_next_value: str
    safe_to_submit: bool
    should_abandon: bool
