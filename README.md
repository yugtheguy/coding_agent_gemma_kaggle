# Gemma 4 Developer Agent Competition — E00 Baseline

## Project
Google DeepMind / Kaggle Gemma 4 Developer Agent Competition 2026. This repository holds the source code and configurations for E00 Baseline V1.

## Workflow
Antigravity/local → GitHub → Kaggle → execute/evaluate

GitHub stores source and configuration. Kaggle supplies the competition model, harness, and data. We do NOT duplicate the Kaggle harness locally.
Expensive execution occurs on Kaggle. Future stages will add telemetry, caching/resume, and evaluation tooling.

GitHub = code
Kaggle = heavy execution
runs/cache = runtime artifacts

## Kaggle Execution Contract
Any future long-running process must:
- show progress;
- periodically report elapsed time;
- report ETA where estimable;
- expose cache hit/miss behavior;
- checkpoint resumable work where practical;
- avoid silently recomputing completed work.

Future expensive tasks must use configuration-aware cache invalidation.

## Usage
Package submission:
```bash
python scripts/package_submission.py
```

Run tests:
```bash
pytest -q
```

Local infrastructure test (Dry Run):
```bash
python scripts/run_e00.py --config experiments/E00.yaml --dry-run --tasks 10
```

Resume example:
```bash
python scripts/run_e00.py --config experiments/E00.yaml --dry-run --tasks 10 --resume <run_id>
```

Summary:
```bash
python scripts/summarize_runs.py runs/<run_id>
```

Kaggle workflow:
```bash
git clone https://github.com/yugtheguy/coding_agent_gemma_kaggle.git
# or
git pull origin main
```
Then run project scripts.
