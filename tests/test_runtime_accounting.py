from src.control.runtime_accounting import RuntimeAccounting, GlobalBudgetContext

def test_runtime_accounting():
    acc = RuntimeAccounting(agent_active_seconds=10.0, task_end_to_end_seconds=15.0)
    assert acc.agent_active_seconds == 10.0
    
def test_global_budget_context():
    ctx = GlobalBudgetContext(global_remaining_seconds=1000.0, tasks_remaining=5)
    assert ctx.get_available_average_seconds() == 200.0
    
    ctx2 = GlobalBudgetContext(global_remaining_seconds=1000.0, tasks_remaining=0)
    assert ctx2.get_available_average_seconds() == 0.0
