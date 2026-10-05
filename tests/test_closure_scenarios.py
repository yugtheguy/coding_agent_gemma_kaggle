import pytest
from src.agent.state import Phase, AgentState
from src.controller.task_controller import TaskController, ControllerConfig
from src.control.runtime_accounting import GlobalBudgetContext
from src.controller.controller_backends import ControllerBackends, TaskInput

def test_illegal_transition():
    state = AgentState()
    state.phase = Phase.UNDERSTAND
    with pytest.raises(ValueError) as exc:
        state.transition_to(Phase.PATCH)
    assert "Invalid transition" in str(exc.value)

def test_context_limit():
    # Simulate a provider raising context overflow
    class OversizedMock:
        def localize(self, state):
            raise Exception("INFRA_CONTEXT_OVERFLOW")
            
    backends = ControllerBackends(localization_provider=OversizedMock())
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test_ctx", "issue", "repo"), "run_ctx")
    assert res.final_phase == "ABANDONED"
    assert "INFRA_CONTEXT_OVERFLOW" in res.infra_failure

def test_step_limit():
    class StallingMock:
        def localize(self, state):
            return "READY" # Force it into a loop that never progresses
        def diagnose(self, state):
            return "READY"
        def generate_patch(self, state): pass
        def run_target(self): return "FAIL"
            
    backends = ControllerBackends(
        localization_provider=StallingMock(),
        diagnosis_provider=StallingMock(),
        patch_provider=StallingMock(),
        command_backend=StallingMock()
    )
    
    # max_steps=5
    config = ControllerConfig(max_steps=5)
    ctrl = TaskController(backends, config, GlobalBudgetContext(1, 3600, 3600))
    # Provide enough hard_patch_attempts so it hits step limit before budget limit
    ctrl.budget_config.hard_patch_attempts = 10
    res = ctrl.run(TaskInput("test_stall", "issue", "repo"), "run_stall")
    
    assert res.final_phase == "ABANDONED"
    assert res.termination_reason == "CONTROLLER_STEP_LIMIT"
    assert res.trajectory_event_count == 5

def test_budget_accounting():
    class CountMock:
        def localize(self, state): 
            # Simulate a semantic call
            state.budget.semantic_calls_used += 1
            return "PASS"
        def diagnose(self, state): return "READY"
        def generate_patch(self, state): pass
        def run_target(self): return "PASS"
        def run_regression(self): return "PASS"
        
    backends = ControllerBackends(
        localization_provider=CountMock(),
        diagnosis_provider=CountMock(),
        patch_provider=CountMock(),
        command_backend=CountMock(),
        submission_backend=None
    )
    ctrl = TaskController(backends, ControllerConfig(), GlobalBudgetContext(1, 3600, 3600))
    res = ctrl.run(TaskInput("test_acct", "issue", "repo"), "run_acct")
    
    assert res.model_turns == 2 # DIAGNOSE, PATCH
    assert res.tool_calls == 3 # LOCALIZE, VERIFY_TARGET, VERIFY_REGRESSION
    assert res.semantic_calls == 1
    assert res.graph_calls == 0
    assert res.patch_attempts == 1

def test_backend_mode_safety():
    class FakeSemanticBackend: pass
    backends = ControllerBackends(semantic_backend=FakeSemanticBackend())
    
    # Should raise Exception when initialized in harness mode
    config = ControllerConfig(mode="harness", fail_on_missing_harness_binding=True)
    with pytest.raises(Exception) as exc:
        TaskController(backends, config)
    assert "INFRA_HARNESS_BINDING_ERROR" in str(exc.value)
