from src.agent.recovery_controller import RecoveryController
from src.agent.state import AgentState
from src.recovery.repetition_guard import ActionSignature
import pytest

def test_recovery_controller_process_target_failure():
    controller = RecoveryController()
    state = AgentState()
    state.budget.patch_attempts_used = 1
    state.budget.hard_patch_attempts = 2
    
    decision = controller.process_target_failure(state, "TARGET_FAILED_SAME_REASON", has_new_evidence=False)
    assert decision.action == "REVISIT_DIAGNOSIS"
    assert state.phase == "DIAGNOSE"
    
    decision = controller.process_target_failure(state, "TARGET_FAILED_NEW_REASON", has_new_evidence=True)
    assert decision.action == "ALLOW_REPAIR"
    assert state.phase == "PATCH"
    
    decision = controller.process_target_failure(state, "TARGET_FAILED_NEW_REASON", has_new_evidence=False)
    assert decision.action == "REVISIT_DIAGNOSIS"
    assert state.phase == "DIAGNOSE"
    
    decision = controller.process_target_failure(state, "ENVIRONMENT_ERROR", has_new_evidence=False)
    assert decision.action == "STALL"
    assert state.phase == "STALLED"
    
def test_recovery_controller_process_target_success():
    controller = RecoveryController()
    state = AgentState()
    
    decision = controller.process_target_success(state, "CLEAN", has_many_callers=False, is_core_utility=False)
    assert decision.action == "VERIFY_REGRESSION"
    assert state.phase == "VERIFY_REGRESSION"
    assert decision.verification_level == 2
