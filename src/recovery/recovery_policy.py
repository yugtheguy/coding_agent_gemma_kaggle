from src.recovery.recovery_decision import RecoveryDecision
from src.recovery.repetition_guard import ActionSignature, RepetitionGuard

def determine_patch_repair(patch_attempts: int, has_new_evidence: bool, is_materially_different: bool, max_patch_attempts: int) -> RecoveryDecision:
    if patch_attempts >= max_patch_attempts:
        return RecoveryDecision("STALL", "budget exhausted", "STALLED", False, False, "EXPENSIVE", "", 0, True, "")
        
    if not has_new_evidence:
        return RecoveryDecision("PATCH_REPAIR_BLOCKED", "no new evidence", "DIAGNOSE", True, False, "NONE", "", 0, False, "")
        
    if not is_materially_different:
        return RecoveryDecision("PATCH_REPAIR_BLOCKED", "not materially different", "PATCH", True, False, "NONE", "", 0, False, "")
        
    return RecoveryDecision("PATCH_REPAIR_ALLOWED", "justified", "PATCH", True, True, "MEDIUM", "repair logic", 0, False, "")

def handle_search_recovery(guard: RepetitionGuard, sig: ActionSignature) -> RecoveryDecision:
    reason = guard.get_block_reason(sig)
    if reason:
        return RecoveryDecision(reason, reason.lower().replace('_', ' '), "LOCALIZE", False, True, "CHEAP", "semantic search", 0, False, "")
    return RecoveryDecision("RETRY_SEARCH", "allow retry", "LOCALIZE", False, True, "CHEAP", "search results", 0, False, "")

def handle_graph_recovery(noisy: bool) -> RecoveryDecision:
    if noisy:
        return RecoveryDecision("STOP_GRAPH", "noisy graph", "LOCALIZE", False, True, "NONE", "", 0, False, "")
    return RecoveryDecision("CONTINUE_GRAPH", "clean", "LOCALIZE", False, True, "MEDIUM", "graph results", 0, False, "")
