def assess_continuation_value(
    information_gain: str,
    phase: str,
    patch_readiness: bool,
    verification_proximity: bool,
    budget_remaining: float,
    global_average_available: float,
    current_task_seconds: float
) -> str:
    under_pressure = False
    if global_average_available > 0 and current_task_seconds > global_average_available:
        under_pressure = True
        
    if under_pressure and not patch_readiness and not verification_proximity:
        if information_gain not in ["HIGH", "MEDIUM"]:
            return "LOW"
            
    if information_gain == "HIGH":
        return "HIGH"
    
    if patch_readiness and verification_proximity and budget_remaining > 0:
        return "HIGH"
        
    if information_gain == "MEDIUM":
        return "MEDIUM"
        
    if information_gain == "LOW":
        return "LOW"
        
    return "NONE"
