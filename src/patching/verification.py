from dataclasses import dataclass
from typing import Optional
from src.patching.patch_backend import EditBackend
import time

@dataclass
class VerificationResult:
    command: str
    status: str 
    exit_code: int
    duration_seconds: float
    timed_out: bool
    tests_collected: int
    tests_passed: int
    tests_failed: int
    failure_summary: str
    traceback_summary: str
    behavior_observed: str
    supports_patch: bool
    contradicts_patch: bool

def run_syntax_check(backend: EditBackend, path: str) -> bool:
    if not path.endswith('.py'):
        return True
    res = backend.run_command(f"python -m py_compile {path}")
    if "SyntaxError" in res or "IndentationError" in res:
        return False
    return True

def classify_target_failure(
    same_reason: bool, 
    timeout: bool, 
    syntax_error: bool,
    environment_error: bool
) -> str:
    if syntax_error:
        return "SYNTAX_FAILED"
    if environment_error:
        return "INFRA/ENVIRONMENT"
    if timeout:
        return "TARGET_TIMEOUT"
    if same_reason:
        return "TARGET_FAILED_SAME_REASON"
    return "TARGET_FAILED_NEW_REASON"
