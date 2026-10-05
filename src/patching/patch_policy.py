def evaluate_patch_readiness(
    patch_readiness: str,
    location: str,
    invariant: str,
    patch_attempts_used: int,
    hard_model_turns: int,
    is_hard_attempt: bool = False
) -> str:
    if patch_readiness != "READY":
        return "NOT_READY"
    if not location:
        return "NO_LOCATION"
    if not invariant:
        return "NO_INVARIANT"
        
    limit = 2 if is_hard_attempt else 1
    if patch_attempts_used >= limit:
        return "PATCH_BUDGET_EXHAUSTED"
        
    if hard_model_turns <= 0:
        return "MODEL_BUDGET_EXHAUSTED"
        
    return "READY_FOR_PATCH"
