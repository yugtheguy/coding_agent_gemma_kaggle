import os
import glob

def cleanup_agent_artifacts(known_patterns: list = None) -> int:
    if known_patterns is None:
        known_patterns = ["gemma_repro_*.py", "scratch*.py", "tmp*.txt", "debug*.log"]
        
    cleaned = 0
    for pattern in known_patterns:
        for f in glob.glob(pattern):
            if os.path.isfile(f):
                os.remove(f)
                cleaned += 1
    return cleaned
