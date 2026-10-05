from typing import Dict, Any, Optional
from src.control.task_status import TaskStatus, Action
from src.control.termination_decision import TerminationDecision
from src.control.budget_controller import BudgetController, BudgetState
from src.control.runtime_accounting import GlobalBudgetContext

class TerminationController:
    def __init__(self, budget_controller: BudgetController):
        self.budget_controller = budget_controller

    def evaluate(
        self,
        budget_state: BudgetState,
        global_context: GlobalBudgetContext,
        verification_state: Dict[str, Any],
        information_gain: str,
        phase: str,
        infra_failure: Optional[str] = None,
        localization_exhausted: bool = False,
        hypothesis_exhausted: bool = False,
        no_info_actions: int = 0,
        post_success_action_requested: bool = False
    ) -> TerminationDecision:
        from src.control.continuation_value import assess_continuation_value
        
        soft_limit = self.budget_controller.is_soft_limit_reached(budget_state)
        hard_limit = self.budget_controller.is_hard_limit_reached(budget_state)
        
        patch_nonempty = verification_state.get("patch_nonempty", False)
        target_pass = verification_state.get("target_pass", False)
        nearby_pass = verification_state.get("nearby_pass", False)
        risk_low = verification_state.get("risk_low", True)
        
        patch_readiness = patch_nonempty and target_pass
        verification_proximity = patch_readiness and not nearby_pass
        sufficient_verification = patch_readiness and nearby_pass and risk_low
        
        budget_remaining = self.budget_controller.config.hard_task_seconds - budget_state.elapsed_task_seconds
        
        cv = assess_continuation_value(
            information_gain, phase, patch_readiness, verification_proximity,
            budget_remaining, global_context.get_available_average_seconds(), budget_state.elapsed_task_seconds
        )
        
        # Actions after success blocked
        if post_success_action_requested and sufficient_verification:
            return self._build(TaskStatus.SOLVED, Action.SUBMIT_CANDIDATE, "SUFFICIENT_VERIFICATION", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, True, False)
            
        if infra_failure:
            return self._build(TaskStatus.STALLED, Action.ABANDON, infra_failure, budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
            
        if sufficient_verification:
            return self._build(TaskStatus.SOLVED, Action.SUBMIT_CANDIDATE, "SUFFICIENT_VERIFICATION", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, True, False)

        if hard_limit:
            if patch_readiness:
                return self._build(TaskStatus.SOLVED, Action.SUBMIT_CANDIDATE, "HARD_BUDGET_EXHAUSTED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, True, False)
            return self._build(TaskStatus.STALLED, Action.ABANDON, "HARD_BUDGET_EXHAUSTED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
            
        if budget_state.patch_attempts >= 2 and information_gain not in ["HIGH"]:
            return self._build(TaskStatus.STALLED, Action.ABANDON, "PATCH_ATTEMPTS_EXHAUSTED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
            
        if no_info_actions >= 3 and cv not in ["HIGH"]:
            return self._build(TaskStatus.STALLED, Action.ABANDON, "NO_INFORMATION_GAIN", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)

        if localization_exhausted and not verification_proximity and cv not in ["HIGH"]:
            return self._build(TaskStatus.STALLED, Action.ABANDON, "LOCALIZATION_EXHAUSTED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
            
        if hypothesis_exhausted and cv not in ["HIGH"]:
             return self._build(TaskStatus.STALLED, Action.ABANDON, "HYPOTHESIS_EXHAUSTED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
             
        if soft_limit:
            if cv == "HIGH":
                return self._build(TaskStatus.STILL_INFORMATION_GAINING, Action.CONTINUE, "SOFT_BUDGET_ESCALATION_ALLOWED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, False)
            return self._build(TaskStatus.STALLED, Action.ABANDON, "SOFT_LIMIT_REACHED", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, True)
            
        if cv in ["HIGH", "MEDIUM"]:
            return self._build(TaskStatus.STILL_INFORMATION_GAINING, Action.CONTINUE, "HIGH_VALUE_ACTION_REMAINS", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, False)
            
        return self._build(TaskStatus.STILL_INFORMATION_GAINING, Action.CONTINUE, "CONTINUE_NORMAL", budget_state, verification_state, information_gain, budget_remaining, hard_limit, soft_limit, cv, False, False)

    def _build(self, status, action, reason, b_state, v_state, ig, time_rem, hard, soft, cv, safe, abandon) -> TerminationDecision:
        return TerminationDecision(
            task_status=status,
            action=action,
            reason=reason,
            budget_state=b_state.__dict__,
            verification_state=v_state,
            information_gain_state={"information_gain": ig},
            time_remaining=time_rem,
            hard_limit_reached=hard,
            soft_limit_reached=soft,
            expected_next_value=cv,
            safe_to_submit=safe,
            should_abandon=abandon
        )
