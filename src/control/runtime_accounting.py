from dataclasses import dataclass

@dataclass
class RuntimeAccounting:
    agent_active_seconds: float = 0.0
    task_end_to_end_seconds: float = 0.0
    setup_seconds: float = 0.0
    model_startup_seconds: float = 0.0
    repository_setup_seconds: float = 0.0
    patch_extraction_seconds: float = 0.0
    cleanup_seconds: float = 0.0

@dataclass
class GlobalBudgetContext:
    global_elapsed_seconds: float = 0.0
    global_remaining_seconds: float = 0.0
    tasks_completed: int = 0
    tasks_remaining: int = 0
    observed_mean_task_seconds: float = 0.0
    
    def get_available_average_seconds(self) -> float:
        if self.tasks_remaining <= 0:
            return 0.0
        return self.global_remaining_seconds / self.tasks_remaining
