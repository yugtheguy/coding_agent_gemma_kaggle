import time
import traceback
from typing import Dict, Any

from src.agent.state import AgentState, Phase, TaskState
from src.control.task_status import TaskStatus
from src.controller.controller_config import ControllerConfig
from src.controller.controller_result import ControllerResult
from src.controller.controller_backends import TaskInput, ControllerBackends
from src.controller.phase_dispatch import dispatch_phase
from src.control.budget_controller import BudgetConfig, BudgetController
from src.control.runtime_accounting import GlobalBudgetContext
from src.agent.termination_controller import TerminationController

class TaskController:
    def __init__(self, backends: ControllerBackends, config: ControllerConfig, global_budget: GlobalBudgetContext = None, telemetry_logger=None):
        self.backends = backends
        self.config = config
        self.global_budget = global_budget or GlobalBudgetContext(1, 3600, 3600)
        self.logger = telemetry_logger
        self.step_count = 0
        self.start_time = 0.0
        self.budget_config = BudgetConfig()
        self.budget_controller = BudgetController(self.budget_config)
        self.term_ctrl = TerminationController(self.budget_controller)
        
        if self.config.mode == "harness" and self.config.fail_on_missing_harness_binding:
            for b_name in ["semantic_backend", "graph_backend", "localization_provider", "diagnosis_provider", "patch_provider", "submission_backend"]:
                backend = getattr(self.backends, b_name, None)
                if backend is not None:
                    cls_name = backend.__class__.__name__
                    if "Fake" in cls_name or "Mock" in cls_name:
                        raise Exception(f"INFRA_HARNESS_BINDING_ERROR: {b_name} is mock")
        self.last_decision = None
        
    def _log(self, event_type: str, payload: dict, run_id: str, task_id: str):
        if self.logger:
            self.logger.log_event(run_id, event_type, payload, task_id)
            
    def run(self, task: TaskInput, run_id: str) -> ControllerResult:
        self.start_time = time.time()
        self.step_count = 0
        self.last_decision = None
        
        state = AgentState()
        state.task = TaskState(task.task_id, task.issue_text, task.optional_hints, task.repository_path)
        
        self._log("TASK_STARTED", {"task_id": task.task_id}, run_id, task.task_id)
        
        while state.phase not in [Phase.DONE, Phase.ABANDONED]:
            if self.step_count >= self.config.max_steps:
                self._log("CONTROLLER_ERROR", {"reason": "CONTROLLER_STEP_LIMIT"}, run_id, task.task_id)
                self.infra_failure = "CONTROLLER_STEP_LIMIT"
                state.transition_to(Phase.ABANDONED, self.logger, run_id)
                break
                
            self.step_count += 1
            self._log("PHASE_ENTERED", {"phase": state.phase.name}, run_id, task.task_id)
            
            try:
                dispatch_phase(self, state, run_id, task.task_id)
            except Exception as e:
                self._log("CONTROLLER_ERROR", {"error": str(e), "traceback": traceback.format_exc()}, run_id, task.task_id)
                self.infra_failure = str(e)
                state.transition_to(Phase.ABANDONED, self.logger, run_id)
                break
                
            self._log("PHASE_COMPLETED", {"phase": state.phase.name}, run_id, task.task_id)
            
        task_status = "SOLVED" if state.phase == Phase.DONE else "STALLED"
        submission_status = "SUBMITTED" if state.phase == Phase.DONE else "NONE"
        term_reason = "SUCCESS" if state.phase == Phase.DONE else "ABANDONED"
        if getattr(self, "infra_failure", None) == "CONTROLLER_STEP_LIMIT":
            term_reason = "CONTROLLER_STEP_LIMIT"
        elif getattr(self, "infra_failure", None) is not None:
            term_reason = "INFRA_FAILURE"
        elif self.last_decision and self.last_decision.reason:
            term_reason = self.last_decision.reason
            
        patch_hash = state.patch.last_patch_summary if state.patch.last_patch_summary else ""
            
        return ControllerResult(
            task_id=task.task_id,
            final_phase=state.phase.name,
            task_status=task_status,
            submission_status=submission_status,
            termination_reason=term_reason,
            patch_hash=patch_hash,
            resolved_locally=state.phase == Phase.DONE,
            infra_failure=getattr(self, "infra_failure", None),
            elapsed_seconds=time.time() - self.start_time,
            model_turns=state.budget.model_turns_used,
            tool_calls=state.budget.tool_calls_used,
            semantic_calls=state.budget.semantic_calls_used,
            graph_calls=0,
            patch_attempts=state.patch.patch_attempts,
            trajectory_event_count=self.step_count
        )
