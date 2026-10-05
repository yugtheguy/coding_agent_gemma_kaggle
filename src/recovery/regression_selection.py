from dataclasses import dataclass
from typing import List

@dataclass
class RegressionResult:
    level: int
    commands: List[str]
    tests_run: int
    tests_passed: int
    tests_failed: int
    timed_out: bool
    environment_error: bool
    duration_seconds: float
    new_failures: int
    known_failures: int
    supports_patch: bool
    risk_remaining: str

def select_nearby_regression_targets(patch_path: str, max_targets: int = 3) -> List[str]:
    if not patch_path:
        return []
    # simplified mock selection
    base_name = patch_path.split("/")[-1].replace(".py", "")
    return [f"pytest -q tests/test_{base_name}.py"][:max_targets]

def assess_regression_risk(patch_scope: str, has_many_callers: bool, is_core_utility: bool) -> str:
    if is_core_utility or has_many_callers or patch_scope == "SUSPICIOUS":
        return "HIGH"
    if patch_scope == "CLEAN":
        return "LOW"
    return "MEDIUM"
