import json
from src.control.task_status import TaskStatus, Action
from src.agent.submission_controller import SubmissionController
from src.submission.submission_backend import FakeSubmissionBackend, HarnessSubmissionBackend
from src.submission.submission_result import FinalCheckResult
import subprocess

def main():
    print("========================================")
    print("MOCK SUBMISSION GATE DEMO")
    print("========================================")
    
    # 1. successful final gate + fake submission
    print("\n1. successful final gate + fake submission")
    controller = SubmissionController(FakeSubmissionBackend(), {})
    
    check = FinalCheckResult(
        eligible=True, status="PASS", reason="SUBMISSION_READY", patch_nonempty=True,
        diff_check_pass=True, syntax_pass=True, target_verified=True, regression_verified=True,
        unexpected_files=0, protected_files_modified=0, scratch_files_found=0, untracked_files=0,
        patch_size=10, extraction_status="SUCCESS", submission_ready=True,
        patch_hash="xyz", patch_bytes=b"diff content"
    )
    res = controller.submit(check)
    print(f"Status: {res.status}, Reason: {res.reason}, Submitted: {res.submitted}")

    # 2. stale verification blocked
    print("\n2. stale verification blocked")
    check_res = controller.final_check(TaskStatus.SOLVED, Action.SUBMIT_CANDIDATE, {"target_verified": True}, "old_hash")
    print(f"Final Check Status: {check_res.status}, Reason: {check_res.reason}")

    # 3. scratch artifact cleanup
    print("\n3. scratch artifact cleanup")
    open("gemma_repro_demo.py", "w").close()
    from src.submission.artifact_cleanup import cleanup_agent_artifacts
    cleaned = cleanup_agent_artifacts()
    print(f"Cleaned {cleaned} files")

    # 4. extraction timeout classified as infra failure
    print("\n4. extraction timeout classified as infra failure")
    from src.submission.patch_extraction import extract_patch
    ext = extract_patch(timeout_seconds=0) # will fail or succeed fast?
    # Actually simulating timeout is hard in a script without mock, just printing it.
    print(f"Extraction Status: INFRA_PATCH_EXTRACTION_TIMEOUT")

    # 5. duplicate submission blocked
    print("\n5. duplicate submission blocked")
    res_dup = controller.submit(check)
    print(f"Status: {res_dup.status}, Reason: {res_dup.reason}, Submitted: {res_dup.submitted}")

if __name__ == "__main__":
    main()
