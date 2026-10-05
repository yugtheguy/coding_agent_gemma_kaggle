import pytest
from src.agent.budget_state import BudgetState

def test_budget_counters():
    budget = BudgetState()
    budget.record_model_turn()
    budget.record_tool_call()
    budget.update_elapsed(10)
    
    assert budget.model_turns_used == 1
    assert budget.tool_calls_used == 1
    assert budget.elapsed_seconds == 10

def test_soft_limit_detection():
    budget = BudgetState(soft_model_turns=2)
    assert not budget.soft_limit_reached
    budget.record_model_turn()
    assert not budget.soft_limit_reached
    budget.record_model_turn()
    assert budget.soft_limit_reached

def test_hard_limit_detection():
    budget = BudgetState(hard_task_seconds=100)
    budget.update_elapsed(101)
    assert budget.hard_limit_reached
