def get_next_verification_level(current_level: int, risk: str, budget_allows_full: bool) -> int:
    if current_level < 2:
        return current_level + 1
        
    if current_level == 2:
        if risk == "HIGH":
            return 3
        if risk == "LOW":
            return -1 
            
    if current_level == 3:
        if budget_allows_full:
            return 4
        return -1
        
    return -1
