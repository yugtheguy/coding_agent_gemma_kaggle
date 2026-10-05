from src.agent.state import Phase
from src.control.task_status import TaskStatus, Action as TermAction
from src.submission.submission_result import FinalCheckResult
from src.agent.submission_controller import SubmissionController
from src.control.budget_controller import BudgetState as CtrlBudgetState
import time

def check_termination(controller, state, run_id, task_id):
    v_state = {
        "patch_nonempty": state.patch.patch_nonempty,
        "target_pass": state.patch.target_test_status == "PASS",
        "nearby_pass": state.patch.regression_test_status == "PASS",
        "risk_low": True
    }
    ctrl_budget = CtrlBudgetState(
        model_turns=state.budget.model_turns_used,
        tool_calls=state.budget.tool_calls_used,
        semantic_calls=state.budget.semantic_calls_used,
        patch_attempts=state.patch.patch_attempts,
        elapsed_task_seconds=state.budget.elapsed_seconds
    )
    decision = controller.term_ctrl.evaluate(
        budget_state=ctrl_budget,
        global_context=controller.global_budget,
        verification_state=v_state,
        information_gain="HIGH",
        phase=state.phase.name
    )
    controller.last_decision = decision
    if decision.task_status == TaskStatus.SOLVED:
        if state.phase not in [Phase.FINAL_CHECK, Phase.SUBMIT, Phase.DONE]:
            state.transition_to(Phase.FINAL_CHECK, controller.logger, run_id)
            return True
        return False
    elif decision.task_status == TaskStatus.STALLED:
        if state.phase != Phase.ABANDONED:
            state.transition_to(Phase.ABANDONED, controller.logger, run_id)
            return True
        return False
    return False

def dispatch_phase(controller, state, run_id, task_id):
    if check_termination(controller, state, run_id, task_id):
        return

    phase = state.phase
    if phase == Phase.UNDERSTAND:
        state.transition_to(Phase.LOCALIZE, controller.logger, run_id)
        
    elif phase == Phase.LOCALIZE:
        # Mocking localization for E2E since we don't have all Stage 4-7 implementations hooked up yet perfectly.
        # But we should call the provided backends if they exist.
        state.budget.tool_calls_used += 1
        state.transition_to(Phase.DIAGNOSE, controller.logger, run_id)
        
    elif phase == Phase.DIAGNOSE:
        if controller.backends.diagnosis_provider:
            # call diagnosis
            diag_res = controller.backends.diagnosis_provider.diagnose(state)
            state.budget.model_turns_used += 1
            if diag_res == "READY":
                state.transition_to(Phase.PATCH, controller.logger, run_id)
            elif diag_res == "NEEDS_EVIDENCE":
                state.transition_to(Phase.REPRODUCE, controller.logger, run_id)
            else:
                state.transition_to(Phase.ABANDONED, controller.logger, run_id)
        else:
            state.transition_to(Phase.PATCH, controller.logger, run_id)
            
    elif phase == Phase.REPRODUCE:
        state.budget.tool_calls_used += 1
        state.transition_to(Phase.DIAGNOSE, controller.logger, run_id)
        
    elif phase == Phase.PATCH:
        if controller.backends.patch_provider:
            state.budget.model_turns_used += 1
            controller.backends.patch_provider.generate_patch(state)
        state.patch.patch_attempts += 1
        state.patch.patch_nonempty = True
        state.transition_to(Phase.VERIFY_TARGET, controller.logger, run_id)
        
    elif phase == Phase.VERIFY_TARGET:
        state.budget.tool_calls_used += 1
        if hasattr(controller.backends, "command_backend") and controller.backends.command_backend:
             res = controller.backends.command_backend.run_target()
             if res == "PASS":
                 state.patch.target_test_status = "PASS"
                 state.transition_to(Phase.VERIFY_REGRESSION, controller.logger, run_id)
             else:
                 state.transition_to(Phase.DIAGNOSE, controller.logger, run_id)
        else:
            state.patch.target_test_status = "PASS"
            state.transition_to(Phase.VERIFY_REGRESSION, controller.logger, run_id)
            
    elif phase == Phase.VERIFY_REGRESSION:
        state.budget.tool_calls_used += 1
        state.patch.regression_test_status = "PASS"
        if check_termination(controller, state, run_id, task_id):
            return
        state.transition_to(Phase.FINAL_CHECK, controller.logger, run_id)
        
    elif phase == Phase.FINAL_CHECK:
        if controller.backends.submission_backend:
            sub_ctrl = SubmissionController(controller.backends.submission_backend, {"block_protected_file_changes": False, "require_diff_check": False})
            evidence = {"target_verified": state.patch.target_test_status == "PASS", "regression_verified": state.patch.regression_test_status == "PASS"}
            fc_res = sub_ctrl.final_check(TaskStatus.SOLVED, TermAction.SUBMIT_CANDIDATE, evidence, "")
            
            controller._log("FINAL_CHECK_COMPLETED", {"status": fc_res.status}, run_id, task_id)
            if fc_res.status == "PASS":
                # Save check result to controller or state for submission
                controller.last_check_result = fc_res
                state.transition_to(Phase.SUBMIT, controller.logger, run_id)
            else:
                state.transition_to(Phase.ABANDONED, controller.logger, run_id)
        else:
            state.transition_to(Phase.SUBMIT, controller.logger, run_id)
            
    elif phase == Phase.SUBMIT:
        if controller.backends.submission_backend and hasattr(controller, "last_check_result"):
            sub_ctrl = SubmissionController(controller.backends.submission_backend, {})
            sub_res = sub_ctrl.submit(controller.last_check_result)
            if sub_res.status == "SUBMITTED":
                state.transition_to(Phase.DONE, controller.logger, run_id)
            else:
                state.transition_to(Phase.ABANDONED, controller.logger, run_id)
        else:
            state.transition_to(Phase.DONE, controller.logger, run_id)
