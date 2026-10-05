class ProgressTracker:
    def __init__(self):
        self.actions_after_last_passing_validation = 0
        
    def record_action(self):
        self.actions_after_last_passing_validation += 1
        
    def record_passing_validation(self):
        self.actions_after_last_passing_validation = 0
