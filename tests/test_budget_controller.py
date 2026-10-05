from src.control.budget_controller import BudgetConfig, BudgetState, BudgetController

def test_budget_controller():
    config = BudgetConfig(soft_model_turns=10, hard_model_turns=15)
    controller = BudgetController(config)
    
    state = BudgetState(model_turns=10)
    assert controller.is_soft_limit_reached(state)
    assert not controller.is_hard_limit_reached(state)
    
    state = BudgetState(model_turns=16)
    assert controller.is_soft_limit_reached(state)
    assert controller.is_hard_limit_reached(state)
