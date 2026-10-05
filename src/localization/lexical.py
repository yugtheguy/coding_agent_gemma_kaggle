import subprocess
import shutil
import re
import os
from pathlib import Path
from typing import List, Dict
from .repository_view import RepositoryView

def run_rg(pattern: str, root: Path, fixed_strings: bool = True, ignore_case: bool = False) -> List[Dict]:
    rg_exec = shutil.which("rg")
    if not rg_exec:
        return []
    
    args = [rg_exec, "--json"]
    if fixed_strings:
        args.append("-F")
    if ignore_case:
        args.append("-i")
    
    args.append(pattern)
    args.append(str(root))
    
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
    except Exception:
        return []
    
    hits = []
    for line in result.stdout.splitlines():
        if not line.strip(): continue
        import json
        try:
            data = json.loads(line)
            if data.get("type") == "match":
                m = data["data"]
                # In rg --json, path is under m["path"]["text"]
                path = m["path"]["text"]
                # Make it relative if it's absolute
                if os.path.isabs(path):
                    path = str(Path(path).relative_to(root)).replace("\\", "/")
                lineno = m["line_number"]
                text = m["lines"]["text"].strip()
                hits.append({"path": path, "line": lineno, "text": text})
        except:
            pass
    return hits

def python_fallback_search(pattern: str, root: Path, fixed_strings: bool = True, ignore_case: bool = False) -> List[Dict]:
    hits = []
    repo = RepositoryView(root)
    files = repo.list_candidate_files()
    
    flags = re.IGNORECASE if ignore_case else 0
    if fixed_strings:
        rx = re.compile(re.escape(pattern), flags)
    else:
        rx = re.compile(pattern, flags)
        
    for path in files:
        content = repo.read_file(path)
        if not content: continue
        
        for i, line in enumerate(content.splitlines(), 1):
            if rx.search(line):
                rel_path = str(path.relative_to(root)).replace("\\", "/")
                hits.append({"path": rel_path, "line": i, "text": line.strip()})
    return hits

def search_text(pattern: str, root: Path, fixed_strings: bool = True, ignore_case: bool = False, backend: str = "auto") -> List[Dict]:
    if backend == "auto":
        if shutil.which("rg"):
            return run_rg(pattern, root, fixed_strings=fixed_strings, ignore_case=ignore_case)
        else:
            return python_fallback_search(pattern, root, fixed_strings=fixed_strings, ignore_case=ignore_case)
    elif backend == "rg":
        return run_rg(pattern, root, fixed_strings=fixed_strings, ignore_case=ignore_case)
    else:
        return python_fallback_search(pattern, root, fixed_strings=fixed_strings, ignore_case=ignore_case)
