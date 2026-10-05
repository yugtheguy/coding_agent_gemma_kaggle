from src.control.continuation_value import assess_continuation_value

def test_assess_continuation_value():
    assert assess_continuation_value("HIGH", "phase", False, False, 100, 200, 50) == "HIGH"
    
    # Under pressure but HIGH info gain
    assert assess_continuation_value("HIGH", "phase", False, False, 100, 100, 150) == "HIGH"
    
    # Under pressure, LOW info gain -> LOW
    assert assess_continuation_value("LOW", "phase", False, False, 100, 100, 150) == "LOW"
    
    # Verification proximity
    assert assess_continuation_value("LOW", "phase", True, True, 100, 200, 50) == "HIGH"
