from src.control.task_status import TaskStatus, Action
from src.submission.submission_result import FinalCheckResult, SubmissionResult
from src.submission.patch_extraction import extract_patch
from src.submission.protected_paths import is_protected, is_test_file
from src.submission.artifact_cleanup import cleanup_agent_artifacts
import subprocess

class SubmissionController:
    def __init__(self, backend, config: dict):
        self.backend = backend
        self.config = config
        self.submitted_hashes = set()
        
    def final_check(self, decision_status: TaskStatus, decision_action: Action, evidence: dict, patch_hash: str) -> FinalCheckResult:
        if decision_status != TaskStatus.SOLVED or decision_action != Action.SUBMIT_CANDIDATE:
            return self._fail("NOT_ELIGIBLE")

        cleanup_agent_artifacts()
            
        res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
        lines = [l for l in res.stdout.strip().split("\n") if l]
        untracked = sum(1 for l in lines if l.startswith("??"))
        
        diff_res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
        changed_files = [f.strip() for f in diff_res.stdout.strip().split("\n") if f.strip()]
        
        protected_mods = sum(1 for f in changed_files if is_protected(f))
        test_mods = sum(1 for f in changed_files if is_test_file(f))
        
        if protected_mods > 0 and self.config.get("block_protected_file_changes", True):
            return self._fail("PROTECTED_FILE_CHANGE", protected_mods=protected_mods)
            
        if test_mods > 0 and self.config.get("block_unexpected_test_changes", True):
            return self._fail("UNEXPECTED_TEST_CHANGE")

        for f in changed_files:
            if f.endswith(".py"):
                syn = subprocess.run(["python", "-m", "py_compile", f], capture_output=True)
                if syn.returncode != 0:
                    return self._fail("SYNTAX_FAIL")
                    
        if not evidence.get("target_verified"):
            return self._fail("TARGET_NOT_VERIFIED")
            
        ext = extract_patch(self.config.get("extraction_timeout", 180))
        if ext["status"] != "SUCCESS":
            return self._fail(ext["status"])
            
        current_hash = ext["patch_hash"]
        if patch_hash and current_hash != patch_hash:
             return self._fail("STALE_VERIFICATION")
             
        diff_check = subprocess.run(["git", "diff", "--check"], capture_output=True)
        diff_pass = diff_check.returncode == 0
        if not diff_pass and self.config.get("require_diff_check", True):
            return self._fail("DIFF_CHECK_FAIL")
        
        return FinalCheckResult(
            eligible=True, status="PASS", reason="SUBMISSION_READY", patch_nonempty=True,
            diff_check_pass=diff_pass, syntax_pass=True, target_verified=True, 
            regression_verified=evidence.get("regression_verified", False),
            unexpected_files=0, protected_files_modified=0, scratch_files_found=0, untracked_files=untracked,
            patch_size=len(ext["patch_bytes"]), extraction_status="SUCCESS", submission_ready=True,
            patch_hash=current_hash, patch_bytes=ext["patch_bytes"]
        )
        
    def _fail(self, reason, protected_mods=0) -> FinalCheckResult:
        is_infra = reason.startswith("INFRA")
        return FinalCheckResult(
            eligible=False, status="INFRA_FAILURE" if is_infra else "FAIL", 
            reason=reason, patch_nonempty=False,
            diff_check_pass=False, syntax_pass=False, target_verified=False, regression_verified=False,
            unexpected_files=0, protected_files_modified=protected_mods, scratch_files_found=0, untracked_files=0,
            patch_size=0, extraction_status=reason if is_infra else "", submission_ready=False
        )

    def submit(self, check: FinalCheckResult) -> SubmissionResult:
        if not check.submission_ready:
            return SubmissionResult("BLOCKED", False, 0, "", 0, "NOT_READY", None, 0.1)
            
        if check.patch_hash in self.submitted_hashes and self.config.get("prevent_duplicate_submission", True):
            return SubmissionResult("BLOCKED", False, 0, check.patch_hash, 0, "DUPLICATE_SUBMISSION", None, 0.1)
            
        try:
            import time
            start = time.time()
            res = self.backend.submit_patch(check.patch_bytes)
            dur = time.time() - start
            if res.get("status") == "SUCCESS":
                self.submitted_hashes.add(check.patch_hash)
                return SubmissionResult("SUBMITTED", True, len(check.patch_bytes), check.patch_hash, 1, "SUCCESS", None, dur)
            else:
                return SubmissionResult("FAILED", False, 0, check.patch_hash, 0, "BACKEND_ERROR", "INFRA_SUBMISSION_FAILURE", dur)
        except RuntimeError as e:
            return SubmissionResult("FAILED", False, 0, check.patch_hash, 0, "INFRA_ERROR", str(e), 0.1)
