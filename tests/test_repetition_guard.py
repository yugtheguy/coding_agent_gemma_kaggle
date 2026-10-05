from src.recovery.repetition_guard import RepetitionGuard, ActionSignature

def test_repetition_guard():
    guard = RepetitionGuard(3)
    sig = ActionSignature("READ", "target", "query", "phase", "hash")
    
    guard.record_action(sig, progress_made=False)
    assert guard.is_action_repeated(sig)
    
    sig2 = ActionSignature("READ", "target2", "query", "phase", "hash")
    assert not guard.is_action_repeated(sig2)
    
    assert not guard.is_blocked(sig2)
    
    guard.record_action(sig, progress_made=False)
    guard.record_action(sig, progress_made=False)
    
    # After 3 no_info actions, everything should be blocked if we rely on max_consecutive_no_info
    sig3 = ActionSignature("READ", "target3", "query", "phase", "hash")
    assert guard.is_blocked(sig3)
