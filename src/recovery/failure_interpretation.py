def interpret_target_failure(failure_type: str, has_new_evidence: bool, patch_attempts: int, max_patch_attempts: int) -> dict:
    if failure_type == "SYNTAX_FAILED":
        return {
            "action": "ALLOW_REPAIR" if patch_attempts < max_patch_attempts else "STALL",
            "requires_new_evidence": False,
            "target_phase": "PATCH" if patch_attempts < max_patch_attempts else "STALLED"
        }
    if failure_type == "ENVIRONMENT_ERROR":
        return {
            "action": "STALL",
            "requires_new_evidence": False,
            "target_phase": "STALLED"
        }
    if failure_type == "TARGET_TIMEOUT":
        return {
            "action": "REVISIT_DIAGNOSIS", 
            "requires_new_evidence": False,
            "target_phase": "DIAGNOSE"
        }
    if failure_type == "TARGET_FAILED_SAME_REASON":
        return {
            "action": "REVISIT_DIAGNOSIS",
            "requires_new_evidence": False,
            "target_phase": "DIAGNOSE"
        }
    if failure_type == "TARGET_FAILED_NEW_REASON":
        return {
            "action": "ALLOW_REPAIR" if patch_attempts < max_patch_attempts and has_new_evidence else "REVISIT_DIAGNOSIS",
            "requires_new_evidence": True,
            "target_phase": "PATCH" if patch_attempts < max_patch_attempts and has_new_evidence else "DIAGNOSE"
        }
    return {
        "action": "STALL",
        "requires_new_evidence": False,
        "target_phase": "STALLED"
    }
