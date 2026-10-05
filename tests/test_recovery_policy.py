from src.recovery.recovery_policy import determine_patch_repair, handle_search_recovery, handle_graph_recovery
from src.recovery.repetition_guard import ActionSignature, RepetitionGuard

def test_determine_patch_repair():
    assert determine_patch_repair(2, True, True, 2).action == "STALL"
    assert determine_patch_repair(1, False, True, 2).action == "PATCH_REPAIR_BLOCKED"
    assert determine_patch_repair(1, True, False, 2).action == "PATCH_REPAIR_BLOCKED"
    assert determine_patch_repair(1, True, True, 2).action == "PATCH_REPAIR_ALLOWED"

def test_handle_search_recovery():
    guard = RepetitionGuard(max_consecutive_no_info=3)
    sig = ActionSignature("SEARCH", "target", "query", "phase", "hash")
    guard.record_action(sig, progress_made=False)
    guard.record_action(sig, progress_made=False)
    guard.record_action(sig, progress_made=False)
    guard.record_action(sig, progress_made=False)
    assert handle_search_recovery(guard, sig).action == "NO_PROGRESS_DETECTED"
    
    # Test REPEATED_ACTION_BLOCKED
    guard_repeat = RepetitionGuard(max_consecutive_no_info=3)
    sig_repeat = ActionSignature("SEARCH", "target", "query", "phase", "hash")
    guard_repeat.record_action(sig_repeat, progress_made=True) # Reset no_info
    assert handle_search_recovery(guard_repeat, sig_repeat).action == "REPEATED_ACTION_BLOCKED"
    
    guard2 = RepetitionGuard(max_consecutive_no_info=3)
    sig2 = ActionSignature("SEARCH", "target2", "query2", "phase", "hash")
    assert handle_search_recovery(guard2, sig2).action == "RETRY_SEARCH"

def test_handle_graph_recovery():
    assert handle_graph_recovery(True).action == "STOP_GRAPH"
    assert handle_graph_recovery(False).action == "CONTINUE_GRAPH"
