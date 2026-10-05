from src.recovery.regression_selection import select_nearby_regression_targets, assess_regression_risk

def test_select_nearby_regression_targets():
    targets = select_nearby_regression_targets("src/foo.py")
    assert len(targets) == 1
    assert "tests/test_foo.py" in targets[0]

def test_assess_regression_risk():
    assert assess_regression_risk("CLEAN", False, False) == "LOW"
    assert assess_regression_risk("SUSPICIOUS", False, False) == "HIGH"
    assert assess_regression_risk("CLEAN", True, False) == "HIGH"
    assert assess_regression_risk("CLEAN", False, True) == "HIGH"
