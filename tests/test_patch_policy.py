from src.patching.patch_policy import evaluate_patch_readiness

def test_evaluate_patch_readiness():
    assert evaluate_patch_readiness("READY", "foo.py:10", "invariant", 0, 5, False) == "READY_FOR_PATCH"
    assert evaluate_patch_readiness("NOT_READY", "foo.py:10", "invariant", 0, 5, False) == "NOT_READY"
    assert evaluate_patch_readiness("READY", "", "invariant", 0, 5, False) == "NO_LOCATION"
    assert evaluate_patch_readiness("READY", "foo.py:10", "", 0, 5, False) == "NO_INVARIANT"
    assert evaluate_patch_readiness("READY", "foo.py:10", "invariant", 1, 5, False) == "PATCH_BUDGET_EXHAUSTED"
    assert evaluate_patch_readiness("READY", "foo.py:10", "invariant", 1, 5, True) == "READY_FOR_PATCH"
    assert evaluate_patch_readiness("READY", "foo.py:10", "invariant", 0, 0, False) == "MODEL_BUDGET_EXHAUSTED"
