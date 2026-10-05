import hashlib
from pathlib import Path
from dataclasses import dataclass

@dataclass
class PreEditSnapshot:
    path: str
    content_hash: str
    content: str
    working_tree_status: str

class EditBackend:
    def read_file(self, path: str, start_line: int, end_line: int) -> str:
        raise NotImplementedError
        
    def edit_file(self, path: str, old_text: str, new_text: str, allow_multiple: bool = False) -> bool:
        raise NotImplementedError
        
    def write_file(self, path: str, content: str) -> bool:
        raise NotImplementedError
        
    def get_status(self) -> str:
        raise NotImplementedError
        
    def run_command(self, command: str) -> str:
        raise NotImplementedError

class LocalEditBackend(EditBackend):
    def __init__(self, root: Path):
        self.root = root
        
    def read_file(self, path: str, start_line: int, end_line: int) -> str:
        full_path = self.root / path
        if not full_path.exists():
            raise FileNotFoundError(path)
        lines = full_path.read_text(encoding='utf-8').splitlines(keepends=True)
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        return "".join(lines[start_idx:end_idx])
        
    def edit_file(self, path: str, old_text: str, new_text: str, allow_multiple: bool = False) -> bool:
        full_path = self.root / path
        if not full_path.exists():
            return False
            
        content = full_path.read_text(encoding='utf-8')
        count = content.count(old_text)
        
        if count == 0:
            return False
            
        if count > 1 and not allow_multiple:
            return False
            
        new_content = content.replace(old_text, new_text, count if allow_multiple else 1)
        full_path.write_text(new_content, encoding='utf-8')
        return True
        
    def write_file(self, path: str, content: str) -> bool:
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        return True
        
    def get_status(self) -> str:
        return "clean"
        
    def run_command(self, command: str) -> str:
        import subprocess
        try:
            result = subprocess.run(command, cwd=self.root, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
            
def capture_snapshot(backend: EditBackend, path: str) -> PreEditSnapshot:
    try:
        content = backend.read_file(path, 1, 1000000)
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        status = backend.get_status()
        return PreEditSnapshot(path, content_hash, content, status)
    except Exception:
        return PreEditSnapshot(path, "", "", "")
