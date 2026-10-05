from dataclasses import dataclass, field

@dataclass
class ContextConfig:
    target_active_tokens: int = 18000
    hard_active_tokens: int = 24000

@dataclass
class ControllerConfig:
    max_steps: int = 50
    mode: str = "explicit"
    fail_on_missing_harness_binding: bool = True
    prevent_hidden_retries: bool = True
    context: ContextConfig = field(default_factory=ContextConfig)
