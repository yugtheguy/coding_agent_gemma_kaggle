from src.recovery.failure_interpretation import interpret_target_failure

def test_interpret_target_failure():
    assert interpret_target_failure("SYNTAX_FAILED", False, 1, 2)["action"] == "ALLOW_REPAIR"
    assert interpret_target_failure("SYNTAX_FAILED", False, 2, 2)["action"] == "STALL"
    assert interpret_target_failure("ENVIRONMENT_ERROR", False, 1, 2)["action"] == "STALL"
    assert interpret_target_failure("TARGET_TIMEOUT", False, 1, 2)["action"] == "REVISIT_DIAGNOSIS"
    assert interpret_target_failure("TARGET_FAILED_SAME_REASON", False, 1, 2)["action"] == "REVISIT_DIAGNOSIS"
    assert interpret_target_failure("TARGET_FAILED_NEW_REASON", True, 1, 2)["action"] == "ALLOW_REPAIR"
    assert interpret_target_failure("TARGET_FAILED_NEW_REASON", False, 1, 2)["action"] == "REVISIT_DIAGNOSIS"
