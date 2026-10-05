from dataclasses import dataclass, field
from typing import List, Dict, Optional
import hashlib
from pathlib import Path
from src.localization.localization_result import FocusedRead

@dataclass
class SourceSnippet:
    path: str
    line_start: int
    line_end: int
    content: str
    reason: str = ""
    source_evidence_ids: List[str] = field(default_factory=list)
    symbol: str = ""
    truncated: bool = False
    
    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode('utf-8')).hexdigest()

class SourceBackend:
    def read(self, path: str, line_start: int, line_end: int) -> SourceSnippet:
        raise NotImplementedError

class FakeSourceBackend(SourceBackend):
    def __init__(self, root: Path):
        self.root = root
        
    def read(self, path: str, line_start: int, line_end: int) -> SourceSnippet:
        full_path = self.root / path
        if not full_path.exists() or not full_path.is_file():
            return SourceSnippet(path, line_start, line_end, content=f"# FILE NOT FOUND: {path}", truncated=True)
            
        try:
            lines = full_path.read_text(encoding='utf-8').split('\n')
            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), line_end)
            content = '\n'.join(lines[start_idx:end_idx])
            return SourceSnippet(path, line_start, line_end, content=content)
        except Exception as e:
            return SourceSnippet(path, line_start, line_end, content=f"# ERROR READING: {e}", truncated=True)

def merge_reads(reads: List[FocusedRead], merge_overlapping: bool = True) -> List[FocusedRead]:
    if not merge_overlapping or not reads:
        return reads
        
    merged = []
    by_path = {}
    for r in reads:
        by_path.setdefault(r.path, []).append(r)
        
    for path, group in by_path.items():
        group.sort(key=lambda x: x.line_start)
        current = group[0]
        
        for next_read in group[1:]:
            if next_read.line_start <= current.line_end + 5: 
                current.line_end = max(current.line_end, next_read.line_end)
                current.reason += f" | {next_read.reason}"
            else:
                merged.append(current)
                current = next_read
        merged.append(current)
        
    return merged

def acquire_focused_source(
    backend: SourceBackend,
    reads: List[FocusedRead],
    max_files: int = 5,
    max_snippets: int = 6,
    max_lines_per_snippet: int = 120,
    max_total_lines: int = 500,
    telemetry_logger=None,
    run_id: str="",
    task_id: str=""
) -> List[SourceSnippet]:
    
    import time
    start_time = time.time()
    
    merged = merge_reads(reads)
    
    files_seen = set()
    snippets = []
    total_lines = 0
    truncated = False
    
    for r in merged:
        if r.path not in files_seen and len(files_seen) >= max_files:
            truncated = True
            continue
            
        if len(snippets) >= max_snippets:
            truncated = True
            break
            
        lines_requested = r.line_end - r.line_start + 1
        is_snippet_truncated = False
        if lines_requested > max_lines_per_snippet:
            r.line_end = r.line_start + max_lines_per_snippet - 1
            lines_requested = max_lines_per_snippet
            is_snippet_truncated = True
            
        if total_lines + lines_requested > max_total_lines:
            remaining = max_total_lines - total_lines
            if remaining < 10:
                truncated = True
                break
            r.line_end = r.line_start + remaining - 1
            lines_requested = remaining
            truncated = True
            is_snippet_truncated = True
            
        snippet = backend.read(r.path, r.line_start, r.line_end)
        snippet.reason = r.reason
        if is_snippet_truncated:
            snippet.truncated = True
        snippets.append(snippet)
        
        files_seen.add(r.path)
        total_lines += lines_requested
        
    duration = (time.time() - start_time) * 1000
    
    if telemetry_logger and run_id:
        telemetry_logger.log_event(run_id, "SOURCE_ACQUISITION_COMPLETED", {
            "requested_reads": len(reads),
            "merged_reads": len(merged),
            "files_read": len(files_seen),
            "source_lines": total_lines,
            "truncated": truncated,
            "duration_ms": duration
        }, task_id)
        
    return snippets
