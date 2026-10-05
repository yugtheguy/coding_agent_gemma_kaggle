from dataclasses import dataclass

@dataclass
class BudgetConfig:
    soft_model_turns: int = 14
    hard_model_turns: int = 18
    soft_tool_calls: int = 22
    hard_tool_calls: int = 30
    normal_semantic_calls: int = 1
    hard_semantic_calls: int = 2
    normal_graph_calls: int = 3
    hard_graph_calls: int = 5
    normal_patch_attempts: int = 1
    hard_patch_attempts: int = 2
    soft_task_seconds: float = 240.0
    hard_task_seconds: float = 330.0

@dataclass
class BudgetState:
    model_turns: int = 0
    tool_calls: int = 0
    semantic_calls: int = 0
    graph_calls: int = 0
    patch_attempts: int = 0
    elapsed_task_seconds: float = 0.0

class BudgetController:
    def __init__(self, config: BudgetConfig):
        self.config = config

    def is_soft_limit_reached(self, state: BudgetState) -> bool:
        return (state.model_turns >= self.config.soft_model_turns or
                state.tool_calls >= self.config.soft_tool_calls or
                state.elapsed_task_seconds >= self.config.soft_task_seconds)

    def is_hard_limit_reached(self, state: BudgetState) -> bool:
        return (state.model_turns >= self.config.hard_model_turns or
                state.tool_calls >= self.config.hard_tool_calls or
                state.elapsed_task_seconds >= self.config.hard_task_seconds or
                state.patch_attempts >= self.config.hard_patch_attempts)
