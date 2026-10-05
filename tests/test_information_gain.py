from src.recovery.information_gain import assess_information_gain

def test_information_gain():
    assert assess_information_gain("READ_NEW_CALLER", False, "") == "NONE"
    assert assess_information_gain("READ_NEW_CALLER", True, "") == "HIGH"
    assert assess_information_gain("SEMANTIC_SEARCH", True, "BROAD") == "MEDIUM"
    assert assess_information_gain("SAME_READ", True, "") == "NONE"
