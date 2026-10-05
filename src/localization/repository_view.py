from pathlib import Path
from typing import List
import os

IGNORE_DIRS = {
    ".git", "venv", ".venv", "__pycache__", "node_modules", 
    "build", "dist", "cache", "runs", "outputs", "checkpoints", "artifacts"
}

ALLOWED_EXTS = {
    ".py", ".pyi", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".json", ".txt", ".md"
}

class RepositoryView:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        
    def list_candidate_files(self) -> List[Path]:
        candidates = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.')]
            
            for f in filenames:
                ext = Path(f).suffix.lower()
                if ext in ALLOWED_EXTS:
                    candidates.append(Path(dirpath) / f)
        return candidates
        
    def read_file(self, path: Path) -> str:
        try:
            return path.read_text(encoding='utf-8')
        except Exception:
            return ""
