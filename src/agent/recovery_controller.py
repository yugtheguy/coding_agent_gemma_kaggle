from typing import Optional
from src.agent.state import AgentState
from src.recovery.repetition_guard import RepetitionGuard, ActionSignature
from src.recovery.progress_tracker import ProgressTracker
from src.recovery.failure_interpretation import interpret_target_failure
from src.recovery.recovery_decision import RecoveryDecision
from src.recovery.verification_ladder import get_next_verification_level
from src.recovery.regression_selection import select_nearby_regression_targets, assess_regression_risk

class RecoveryController:
    def __init__(self, telemetry_logger=None, run_id: str="", task_id: str=""):
        self.telemetry_logger = telemetry_logger
        self.run_id = run_id
        self.task_id = task_id
        self.repetition_guard = RepetitionGuard()
        self.progress_tracker = ProgressTracker()
        
    def process_target_failure(self, state: AgentState, failure_type: str, has_new_evidence: bool) -> RecoveryDecision:
        self.progress_tracker.record_action()
        patch_attempts = getattr(state.budget, "patch_attempts_used", 0)
        max_attempts = getattr(state.budget, "hard_patch_attempts", 2)
        
        result = interpret_target_failure(failure_type, has_new_evidence, patch_attempts, max_attempts)
        
        if result["action"] == "STALL":
            state.phase = "STALLED"
        elif result["action"] == "ALLOW_REPAIR":
            state.phase = "PATCH"
        elif result["action"] == "REVISIT_DIAGNOSIS":
            state.phase = "DIAGNOSE"
        elif result["action"] == "RUN_TARGET_TEST":
            state.phase = "VERIFY_TARGET"
            
        decision = RecoveryDecision(
            action=result["action"],
            reason="Failure interpretation",
            target_phase=result["target_phase"],
            requires_new_evidence=result["requires_new_evidence"],
            allowed=result["action"] != "STALL",
            cost_class="MEDIUM",
            expected_information="Failure classification",
            verification_level=1,
            stalled=result["action"] == "STALL",
            notes=""
        )
        
        if self.telemetry_logger:
            self.telemetry_logger.log_event(self.run_id, "RECOVERY_DECISION", {"failure": failure_type, "decision": decision.action}, self.task_id)
            
        return decision
        
    def process_target_success(self, state: AgentState, patch_scope: str, has_many_callers: bool, is_core_utility: bool) -> RecoveryDecision:
        self.progress_tracker.record_passing_validation()
        
        risk = assess_regression_risk(patch_scope, has_many_callers, is_core_utility)
        
        next_level = get_next_verification_level(1, risk, False) 
        
        if next_level == 2:
            action = "VERIFY_REGRESSION"
            phase = "VERIFY_REGRESSION"
        elif next_level == -1:
            action = "CONTINUE_TO_FINAL_CHECK"
            phase = "FINAL_CHECK"
        else:
            action = "VERIFY_REGRESSION"
            phase = "VERIFY_REGRESSION"
            
        state.phase = phase
        decision = RecoveryDecision(
            action=action,
            reason=f"Target passed, risk={risk}",
            target_phase=phase,
            requires_new_evidence=False,
            allowed=True,
            cost_class="CHEAP",
            expected_information="Check regressions",
            verification_level=next_level if next_level != -1 else 4,
            stalled=False,
            notes=""
        )
        
        if self.telemetry_logger:
            self.telemetry_logger.log_event(self.run_id, "SUCCESS_CONFIDENCE_REACHED", {"action": action}, self.task_id)
            
        return decision
