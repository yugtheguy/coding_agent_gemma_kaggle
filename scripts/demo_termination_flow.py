import json
from src.control.budget_controller import BudgetConfig, BudgetController, BudgetState
from src.control.runtime_accounting import GlobalBudgetContext
from src.agent.termination_controller import TerminationController

def main():
    print("========================================")
    print("MOCK TERMINATION DEMO")
    print("========================================")
    
    config = BudgetConfig(soft_model_turns=14, hard_model_turns=18)
    controller = TerminationController(BudgetController(config))
    gctx = GlobalBudgetContext(global_remaining_seconds=18000, tasks_remaining=100)
    
    print("\n1. SOLVED")
    dec1 = controller.evaluate(
        BudgetState(elapsed_task_seconds=100), gctx, 
        {"patch_nonempty": True, "target_pass": True, "nearby_pass": True, "risk_low": True},
        "NONE", "VERIFY"
    )
    print(f"Status: {dec1.task_status.name}, Action: {dec1.action.name}, Reason: {dec1.reason}")
    
    print("\n2. STILL_INFORMATION_GAINING")
    dec2 = controller.evaluate(
        BudgetState(elapsed_task_seconds=100), gctx, 
        {"patch_nonempty": False},
        "HIGH", "DIAGNOSE"
    )
    print(f"Status: {dec2.task_status.name}, Action: {dec2.action.name}, Reason: {dec2.reason}")
    
    print("\n3. STALLED")
    dec3 = controller.evaluate(
        BudgetState(elapsed_task_seconds=100), gctx, 
        {"patch_nonempty": False},
        "NONE", "DIAGNOSE", no_info_actions=3
    )
    print(f"Status: {dec3.task_status.name}, Action: {dec3.action.name}, Reason: {dec3.reason}")

    print("\n4. soft-limit high-value continuation")
    dec4 = controller.evaluate(
        BudgetState(model_turns=15), gctx, 
        {"patch_nonempty": False},
        "HIGH", "LOCALIZE"
    )
    print(f"Status: {dec4.task_status.name}, Action: {dec4.action.name}, Reason: {dec4.reason}")

    print("\n5. hard-limit verified submission")
    dec5 = controller.evaluate(
        BudgetState(model_turns=20), gctx, 
        {"patch_nonempty": True, "target_pass": True, "nearby_pass": True},
        "NONE", "VERIFY"
    )
    print(f"Status: {dec5.task_status.name}, Action: {dec5.action.name}, Reason: {dec5.reason}")

    print("\n6. global-budget pressure")
    dec6 = controller.evaluate(
        BudgetState(elapsed_task_seconds=300), gctx, 
        {"patch_nonempty": False},
        "NONE", "LOCALIZE"
    )
    print(f"Status: {dec6.task_status.name}, Action: {dec6.action.name}, Reason: {dec6.reason}")

if __name__ == "__main__":
    main()
