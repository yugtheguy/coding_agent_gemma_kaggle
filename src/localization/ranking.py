import time
import shutil
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from .anchors import Anchor, AnchorType, Confidence as AnchorConfidence, SearchAnchors
from .localization_result import (
    LocalizationHit, MatchType, FileType, Confidence, 
    FileCandidate, SymbolCandidate, LocalizationResult, FocusedRead
)
from .lexical import search_text
from .symbols import extract_symbols_from_ast
from .repository_view import RepositoryView

WEIGHTS = {
    MatchType.EXACT_PATH: 100.0,
    MatchType.PATH_SUFFIX: 50.0,
    MatchType.EXACT_SYMBOL: 50.0,
    MatchType.ERROR_STRING: 40.0,
    MatchType.EXACT_TEXT: 20.0,
    MatchType.LITERAL: 15.0,
    MatchType.CONFIG_KEY: 15.0,
    MatchType.OPERATION: 5.0,
    MatchType.DOMAIN_TERM: 2.0,
    MatchType.TEST_TERM: 3.0,
}

def classify_file_type(path: str) -> FileType:
    if "test" in path.lower() or path.startswith("tests/") or "test_" in path or "_test" in path:
        return FileType.TEST
    if path.endswith(".py") or path.endswith(".pyi"):
        return FileType.SOURCE
    if path.endswith((".toml", ".yaml", ".yml", ".ini", ".cfg", ".json")):
        return FileType.CONFIG
    return FileType.OTHER

def score_hits(hits: List[LocalizationHit]) -> float:
    seen_anchors = defaultdict(int)
    score = 0.0
    for hit in hits:
        count = seen_anchors[hit.anchor_value]
        if count < 3: 
            weight = WEIGHTS.get(hit.match_type, 1.0)
            decay = 1.0 / (count + 1)
            score += weight * decay
            seen_anchors[hit.anchor_value] += 1
    return score

def run_localization(anchors: SearchAnchors, root: Path, backend: str = "auto", telemetry_logger=None, run_id=None, task_id=None) -> LocalizationResult:
    start_time = time.time()
    repo = RepositoryView(root)
    candidates = repo.list_candidate_files()
    candidate_paths = [str(p.relative_to(root)).replace("\\", "/") for p in candidates]
    
    hits: List[LocalizationHit] = []
    stats = {
        "files_scanned": len(candidates),
        "anchors_searched": 0,
        "search_operations": 0,
        "symbol_files_parsed": 0
    }
    
    for a in anchors.anchors:
        if a.anchor_type == AnchorType.FILE_PATH:
            for cp in candidate_paths:
                if cp == a.normalized_value:
                    hits.append(LocalizationHit(cp, 1, None, None, None, a.value, a.anchor_type.name, MatchType.EXACT_PATH, "STRONG", "", WEIGHTS[MatchType.EXACT_PATH], "path_match"))
                elif cp.endswith("/" + a.normalized_value) or cp.endswith("\\" + a.normalized_value) or cp == a.normalized_value:
                    hits.append(LocalizationHit(cp, 1, None, None, None, a.value, a.anchor_type.name, MatchType.PATH_SUFFIX, "STRONG", "", WEIGHTS[MatchType.PATH_SUFFIX], "path_suffix_match"))
            stats["anchors_searched"] += 1
            stats["search_operations"] += 1
            
    grouped_anchors = defaultdict(list)
    for a in anchors.anchors:
        if a.anchor_type == AnchorType.FILE_PATH:
            continue
        grouped_anchors[a.confidence].append(a)
        
    early_stop = False
    
    def search_group(group: List[Anchor], match_type_mapper, ignore_case=False):
        for a in group:
            text_hits = search_text(a.normalized_value, root, fixed_strings=True, ignore_case=ignore_case, backend=backend)
            stats["search_operations"] += 1
            stats["anchors_searched"] += 1
            for th in text_hits:
                hits.append(LocalizationHit(
                    th["path"], th["line"], None, None, None,
                    a.value, a.anchor_type.name, match_type_mapper(a),
                    a.confidence.name, th["text"], WEIGHTS[match_type_mapper(a)], "text_search"
                ))
                
    def get_match_type(a: Anchor) -> MatchType:
        if a.anchor_type == AnchorType.ERROR_MESSAGE: return MatchType.ERROR_STRING
        if a.anchor_type in (AnchorType.STRING_LITERAL, AnchorType.BACKTICKED_TERM): return MatchType.LITERAL
        if a.anchor_type == AnchorType.CONFIG_KEY: return MatchType.CONFIG_KEY
        if a.anchor_type == AnchorType.OPERATION: return MatchType.OPERATION
        if a.anchor_type == AnchorType.DOMAIN_TERM: return MatchType.DOMAIN_TERM
        if a.anchor_type == AnchorType.TEST_CLUE: return MatchType.TEST_TERM
        if a.anchor_type in (AnchorType.IDENTIFIER, AnchorType.DOTTED_NAME, AnchorType.EXCEPTION_NAME):
            return MatchType.EXACT_TEXT
        return MatchType.EXACT_TEXT

    high_conf = grouped_anchors.get(AnchorConfidence.VERY_HIGH, []) + grouped_anchors.get(AnchorConfidence.HIGH, [])
    search_group(high_conf, get_match_type)
    
    file_hits = defaultdict(list)
    for h in hits:
        file_hits[h.path].append(h)
        
    max_score = 0.0
    for path, fhits in file_hits.items():
        s = score_hits(fhits)
        if s > max_score:
            max_score = s
            
    if max_score > 200.0:  
        early_stop = True
    else:
        med_conf = grouped_anchors.get(AnchorConfidence.MEDIUM, []) + grouped_anchors.get(AnchorConfidence.LOW, [])
        search_group(med_conf[:5], get_match_type, ignore_case=True)
                
        file_hits = defaultdict(list)
        for h in hits:
            file_hits[h.path].append(h)
            
    file_candidates = []
    for path, fhits in file_hits.items():
        score = score_hits(fhits)
        ftype = classify_file_type(path)
        anchors_matched = list(set(h.anchor_value for h in fhits))
        summary = list(set(f"{h.match_type.name}: {h.anchor_value}" for h in fhits))
        file_candidates.append(FileCandidate(path, score, 0, ftype, anchors_matched, summary))
        
    file_candidates.sort(key=lambda x: (-x.score, x.path))
    for i, fc in enumerate(file_candidates):
        fc.rank = i + 1
        
    file_candidates = file_candidates[:10]
    
    symbol_hits = []
    for fc in file_candidates[:5]:
        if fc.file_type != FileType.SOURCE:
            continue
        try:
            content = (root / fc.path).read_text(encoding='utf-8')
            syms = extract_symbols_from_ast(content, fc.path)
            stats["symbol_files_parsed"] += 1
            for sym in syms:
                sym_name = sym["name"]
                sym_qual = sym["qualname"]
                # Match against ALL anchors, not just file text hits
                matched_anchor = None
                for a in anchors.anchors:
                    if a.normalized_value == sym_name or a.normalized_value == sym_qual:
                        matched_anchor = a
                        break
                        
                if matched_anchor:
                    # Also add a synthetic hit for the file if it wasn't there
                    if matched_anchor.normalized_value not in fc.matched_anchor_ids:
                        fc.matched_anchor_ids.append(matched_anchor.normalized_value)
                        fc.score += WEIGHTS[MatchType.EXACT_SYMBOL]
                    
                    symbol_hits.append(SymbolCandidate(
                        sym_qual, fc.path, sym["line"], sym["end_line"], sym["kind"],
                        fc.score + WEIGHTS[MatchType.EXACT_SYMBOL], 
                        [matched_anchor.normalized_value],
                        [f"Matched symbol {sym_qual} in top file"]
                    ))
        except Exception:
            pass
            
    symbol_hits.sort(key=lambda x: (-x.score, x.path, x.qualified_name))
    symbol_hits = symbol_hits[:10]
    
    if file_candidates:
        top_score = file_candidates[0].score
        if top_score >= 120.0:
            confidence = Confidence.STRONG
        elif top_score >= 40.0:
            confidence = Confidence.MODERATE
        else:
            confidence = Confidence.WEAK
    else:
        confidence = Confidence.WEAK
        
    stats["files_matched"] = len(file_hits)
    stats["duration_ms"] = (time.time() - start_time) * 1000
    stats["early_stop"] = early_stop
    stats["backend"] = "rg" if shutil.which("rg") and backend in ("auto", "rg") else "python"
    
    focused_reads = []
    for sym in symbol_hits[:3]:
        focused_reads.append(FocusedRead(
            sym.path, max(1, sym.line_start - 5), sym.line_end + 5 if sym.line_end else sym.line_start + 20,
            f"Contains exact {sym.symbol_kind} {sym.qualified_name}"
        ))
    if not focused_reads and file_candidates:
        fc = file_candidates[0]
        for h in file_hits[fc.path]:
            if h.match_type in (MatchType.EXACT_TEXT, MatchType.ERROR_STRING):
                focused_reads.append(FocusedRead(
                    fc.path, max(1, h.line - 20), h.line + 20,
                    f"Surrounding context for {h.anchor_value}"
                ))
                break
                
    result = LocalizationResult(anchors, file_candidates, symbol_hits, stats["backend"], stats, confidence, focused_reads)
    
    if telemetry_logger and run_id and task_id:
        payload = {
            "backend": stats["backend"],
            "anchors_searched": stats["anchors_searched"],
            "search_operations": stats["search_operations"],
            "files_scanned": stats["files_scanned"],
            "files_matched": stats["files_matched"],
            "symbol_files_parsed": stats["symbol_files_parsed"],
            "top_files": [fc.path for fc in file_candidates[:2]],
            "confidence": confidence.name,
            "early_stop": early_stop,
            "duration_ms": stats["duration_ms"]
        }
        telemetry_logger.log_event(run_id, "LEXICAL_LOCALIZATION_COMPLETED", payload, task_id)
        
    return result
