import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def summarize(run_dir: str):
    p = Path(run_dir)
    summary_path = p / "summary.json"
    if not summary_path.exists():
        print(f"No summary found at {summary_path}")
        return
        
    with open(summary_path, "r") as f:
        summary = json.load(f)
        
    events_path = p / "events.jsonl"
    event_count = sum(1 for _ in open(events_path, "r")) if events_path.exists() else 0
    summary["event_count"] = event_count
    
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    summarize(args.run_dir)
