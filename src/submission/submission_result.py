from dataclasses import dataclass
from typing import Optional

@dataclass
class FinalCheckResult:
    eligible: bool
    status: str
    reason: str
    patch_nonempty: bool
    diff_check_pass: bool
    syntax_pass: bool
    target_verified: bool
    regression_verified: bool
    unexpected_files: int
    protected_files_modified: int
    scratch_files_found: int
    untracked_files: int
    patch_size: int
    extraction_status: str
    submission_ready: bool
    patch_hash: str = ""
    patch_bytes: bytes = b""

@dataclass
class SubmissionResult:
    status: str
    submitted: bool
    patch_bytes: int
    patch_hash: str
    files_changed: int
    reason: str
    infra_failure: Optional[str]
    duration_seconds: float
