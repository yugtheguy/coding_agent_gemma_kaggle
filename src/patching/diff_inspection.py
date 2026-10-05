from dataclasses import dataclass
from typing import List, Dict
from src.patching.patch_backend import EditBackend

@dataclass
class DiffInspectionResult:
    files_changed: int
    lines_added: int
    lines_removed: int
    unexpected_files: List[str]
    whitespace_errors: int
    patch_nonempty: bool
    scope: str # CLEAN, SUSPICIOUS, INVALID

def inspect_diff(backend: EditBackend, expected_file: str, max_files: int = 2, max_lines: int = 120) -> DiffInspectionResult:
    out = backend.run_command("git diff --numstat")
    
    files = []
    added = 0
    removed = 0
    
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) == 3:
            add, rem, path = parts
            files.append(path.strip())
            added += int(add) if add != '-' else 0
            removed += int(rem) if rem != '-' else 0
            
    # git uses / everywhere, so normalize
    expected_normalized = expected_file.replace('\\', '/')
    unexpected = [f for f in files if f != expected_normalized]
    
    check_out = backend.run_command("git diff --check")
    whitespace_errors = len([line for line in check_out.split('\n') if "whitespace" in line.lower() or "trailing" in line.lower()])
    
    nonempty = bool(files)
    
    scope = "CLEAN"
    if not nonempty:
        scope = "INVALID"
    elif len(files) > max_files or (added + removed) > max_lines:
        scope = "SUSPICIOUS"
    elif unexpected:
        scope = "SUSPICIOUS"
        
    return DiffInspectionResult(
        files_changed=len(files),
        lines_added=added,
        lines_removed=removed,
        unexpected_files=unexpected,
        whitespace_errors=whitespace_errors,
        patch_nonempty=nonempty,
        scope=scope
    )
