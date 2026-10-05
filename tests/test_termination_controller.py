from src.control.budget_controller import BudgetConfig, BudgetController, BudgetState
from src.control.runtime_accounting import GlobalBudgetContext
from src.agent.termination_controller import TerminationController
from src.control.task_status import TaskStatus, Action

def test_termination_controller_scenarios():
    config = BudgetConfig()
    controller = TerminationController(BudgetController(config))
    gctx = GlobalBudgetContext(global_remaining_seconds=3600, tasks_remaining=10)
    
    # Scenario A: Solved
    decision = controller.evaluate(
        BudgetState(), gctx, 
        {"patch_nonempty": True, "target_pass": True, "nearby_pass": True, "risk_low": True},
        "NONE", "phase"
    )
    assert decision.task_status == TaskStatus.SOLVED
    assert decision.action == Action.SUBMIT_CANDIDATE
    
    # Scenario B: High-value continue
    decision = controller.evaluate(BudgetState(), gctx, {}, "HIGH", "phase")
    assert decision.task_status == TaskStatus.STILL_INFORMATION_GAINING
    
    # Scenario C: No-info stall
    decision = controller.evaluate(BudgetState(), gctx, {}, "NONE", "phase", no_info_actions=3)
    assert decision.task_status == TaskStatus.STALLED
    assert decision.action == Action.ABANDON
    
    # Scenario F: Hard-limit verified
    bstate_hard = BudgetState(model_turns=100)
    decision = controller.evaluate(
        bstate_hard, gctx,
        {"patch_nonempty": True, "target_pass": True, "nearby_pass": True, "risk_low": True},
        "NONE", "phase"
    )
    assert decision.task_status == TaskStatus.SOLVED
    
    # Scenario K: Infra failure
    decision = controller.evaluate(BudgetState(), gctx, {}, "NONE", "phase", infra_failure="INFRA_PATCH_EXTRACTION_FAILURE")
    assert decision.task_status == TaskStatus.STALLED
    assert decision.reason == "INFRA_PATCH_EXTRACTION_FAILURE"
