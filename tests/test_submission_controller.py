from src.control.task_status import TaskStatus, Action
from src.agent.submission_controller import SubmissionController
from src.submission.submission_backend import FakeSubmissionBackend
from src.submission.submission_result import FinalCheckResult

def test_submission_controller_fail_not_eligible():
    controller = SubmissionController(FakeSubmissionBackend(), {})
    res = controller.final_check(TaskStatus.STALLED, Action.ABANDON, {}, "")
    assert res.status == "FAIL"
    assert res.reason == "NOT_ELIGIBLE"

def test_submission_duplicate_blocked():
    controller = SubmissionController(FakeSubmissionBackend(), {})
    check = FinalCheckResult(
        eligible=True, status="PASS", reason="SUBMISSION_READY", patch_nonempty=True,
        diff_check_pass=True, syntax_pass=True, target_verified=True, regression_verified=True,
        unexpected_files=0, protected_files_modified=0, scratch_files_found=0, untracked_files=0,
        patch_size=10, extraction_status="SUCCESS", submission_ready=True,
        patch_hash="abc", patch_bytes=b"abc"
    )
    res1 = controller.submit(check)
    assert res1.status == "SUBMITTED"
    
    res2 = controller.submit(check)
    assert res2.status == "BLOCKED"
    assert res2.reason == "DUPLICATE_SUBMISSION"
