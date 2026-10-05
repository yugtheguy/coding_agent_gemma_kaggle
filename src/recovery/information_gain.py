def assess_information_gain(action_type: str, new_evidence: bool, specificity: str) -> str:
    if not new_evidence:
        return "NONE"
    if action_type in ["READ_NEW_CALLER", "NEW_TRACEBACK", "SPECIFIC_ASSERTION"]:
        return "HIGH"
    if action_type == "SEMANTIC_SEARCH" and specificity == "BROAD":
        return "MEDIUM"
    if action_type == "SAME_READ":
        return "NONE"
    return "LOW"
