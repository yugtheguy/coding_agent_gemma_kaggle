from dataclasses import dataclass

@dataclass
class BudgetState:
    soft_model_turns: int = 14
    hard_model_turns: int = 18
    soft_tool_calls: int = 22
    hard_tool_calls: int = 30
    normal_semantic_calls: int = 1
    hard_semantic_calls: int = 2
    normal_patch_attempts: int = 1
    hard_patch_attempts: int = 2
    soft_task_seconds: int = 240
    hard_task_seconds: int = 330
    
    model_turns_used: int = 0
    tool_calls_used: int = 0
    semantic_calls_used: int = 0
    patch_attempts_used: int = 0
    elapsed_seconds: int = 0

    def record_model_turn(self):
        self.model_turns_used += 1

    def record_tool_call(self):
        self.tool_calls_used += 1

    def record_semantic_call(self):
        self.semantic_calls_used += 1

    def record_patch_attempt(self):
        self.patch_attempts_used += 1

    def update_elapsed(self, seconds: int):
        self.elapsed_seconds += seconds

    @property
    def soft_limit_reached(self) -> bool:
        return (self.model_turns_used >= self.soft_model_turns or
                self.tool_calls_used >= self.soft_tool_calls or
                self.elapsed_seconds >= self.soft_task_seconds)

    @property
    def hard_limit_reached(self) -> bool:
        return (self.model_turns_used >= self.hard_model_turns or
                self.tool_calls_used >= self.hard_tool_calls or
                self.elapsed_seconds >= self.hard_task_seconds)
