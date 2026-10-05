from src.recovery.verification_ladder import get_next_verification_level

def test_get_next_verification_level():
    assert get_next_verification_level(0, "LOW", False) == 1
    assert get_next_verification_level(1, "LOW", False) == 2
    assert get_next_verification_level(2, "HIGH", False) == 3
    assert get_next_verification_level(2, "LOW", False) == -1
    assert get_next_verification_level(3, "MEDIUM", True) == 4
    assert get_next_verification_level(3, "MEDIUM", False) == -1
