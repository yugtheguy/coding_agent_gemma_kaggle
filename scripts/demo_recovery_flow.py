import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.recovery_controller import RecoveryController
from src.agent.state import AgentState
from src.recovery.repetition_guard import ActionSignature

def main():
    print("========================================")
    print("MOCK RECOVERY DEMO - STAGE 10")
    print("========================================\n")
    
    controller = RecoveryController()
    state = AgentState()
    state.budget.hard_patch_attempts = 2
    state.budget.patch_attempts_used = 1
    
    print("Case 1: target passes -> nearby regression passes -> FINAL_CHECK recommended")
    dec1 = controller.process_target_success(state, "CLEAN", False, False)
    print(f"Target passed. Decision: {dec1.action}, Next phase: {dec1.target_phase}, Level: {dec1.verification_level}")
    from src.recovery.verification_ladder import get_next_verification_level
    next_level = get_next_verification_level(2, "LOW", False)
    print(f"Nearby regression passed. Next level: {next_level} -> FINAL_CHECK\n")
    
    print("Case 2: target same failure -> diagnosis revisited")
    dec2 = controller.process_target_failure(state, "TARGET_FAILED_SAME_REASON", has_new_evidence=False)
    print(f"Target failed (same). Decision: {dec2.action}, Next phase: {dec2.target_phase}\n")
    
    print("Case 3: repeated search blocked")
    sig = ActionSignature("SEARCH", "target", "query", "phase", "hash")
    controller.repetition_guard.record_action(sig, False)
    controller.repetition_guard.record_action(sig, False)
    controller.repetition_guard.record_action(sig, False)
    from src.recovery.recovery_policy import handle_search_recovery
    dec3 = handle_search_recovery(controller.repetition_guard, sig)
    print(f"3x Repeated search -> Decision: {dec3.action}\n")
    
    print("Case 4: second patch denied without new evidence")
    state.budget.patch_attempts_used = 1
    from src.recovery.recovery_policy import determine_patch_repair
    dec4 = determine_patch_repair(state.budget.patch_attempts_used, has_new_evidence=False, is_materially_different=True, max_patch_attempts=2)
    print(f"Second patch no new evidence -> Decision: {dec4.action}")
    
if __name__ == "__main__":
    main()
