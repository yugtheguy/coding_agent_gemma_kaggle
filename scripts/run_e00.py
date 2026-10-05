import argparse
import yaml
from pathlib import Path
from src.evaluation.runner import E00Runner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tasks", type=int, default=5)
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()
    
    root_dir = Path(__file__).resolve().parent.parent
    
    with open(root_dir / args.config, "r") as f:
        config = yaml.safe_load(f)
        
    prompt_path = root_dir / "prompts" / "system_e00.md"
    prompt_content = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    
    runner = E00Runner(root_dir, config, prompt_content, resume_run_id=args.resume)
    
    task_ids = [f"synthetic_task_{i}" for i in range(args.tasks)]
    
    print(f"Starting run {runner.ctx.run_id}, mode={'dry_run' if args.dry_run else 'normal'}")
    
    runner.run(task_ids, dry_run=args.dry_run)
    print(f"Finished run {runner.ctx.run_id}")

if __name__ == "__main__":
    main()
