import time
import sys

def format_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

class Progress:
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        
    def update(self, task_id: str, status: str):
        if status == "skipped":
            self.skipped += 1
        elif status == "failed":
            self.failed += 1
        else:
            self.completed += 1
            
        current = self.completed + self.failed + self.skipped
        elapsed = int(time.time() - self.start_time)
        eta = 0
        if current > 0:
            eta = int((elapsed / current) * (self.total - current))
            
        print(f"[{current}/{self.total}] task={task_id}")
        print(f"completed={self.completed} failed={self.failed} skipped={self.skipped}")
        print(f"elapsed={format_time(elapsed)}")
        print(f"ETA={format_time(eta)}")
        print("-" * 40)

class Heartbeat:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.start_time = time.time()
        self.last_beat = self.start_time
        
    def tick(self, message: str = "still running..."):
        now = time.time()
        if now - self.last_beat >= self.interval:
            print(f"{message} elapsed={int(now - self.start_time)}s")
            self.last_beat = now
