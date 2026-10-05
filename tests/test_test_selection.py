from src.patching.test_selection import VerificationTarget

def test_verification_target():
    target = VerificationTarget("pytest", "EXISTING_TEST", "reason", "signal", "CHEAP")
    assert target.command == "pytest"
    assert target.target_type == "EXISTING_TEST"
