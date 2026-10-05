import re
from typing import List, Tuple
from .anchors import Anchor, AnchorType, Confidence, SearchAnchors
from .anchor_normalization import normalize_anchor
from src.agent.state import SearchEvidence

DOMAIN_TERMS = {
    "url", "fragment", "header", "redirect", "cookie", "socket", 
    "iterator", "timezone", "serializer", "schema", "transaction", 
    "ast", "token", "cache", "request", "response", "session"
}

OPERATIONS = {
    "encode", "decode", "serialize", "deserialize", "parse", 
    "normalize", "quote", "unquote", "redirect", "retry", "cache", 
    "sort", "merge", "filter", "validate", "truncate", "resolve", 
    "load", "save", "render", "close"
}

TEST_CLUES_VOCAB = {
    "test", "regression", "fixture", "mock", "expected", "assert", "raises"
}

def extract_anchors(text: str, telemetry_logger=None, run_id: str = None, task_id: str = None) -> SearchAnchors:
    anchors = []
    
    def add(val: str, type_: AnchorType, start: int, end: int, conf: Confidence, prov: str):
        norm = normalize_anchor(val, type_)
        anchors.append(Anchor(val, type_, (start, end), norm, conf, prov))
        
    for m in re.finditer(r'`([^`\n]+)`', text):
        add(m.group(1), AnchorType.BACKTICKED_TERM, m.start(), m.end(), Confidence.VERY_HIGH, "backtick")
        
    for m in re.finditer(r'"([^"\n]{2,})"', text):
        add(m.group(1), AnchorType.STRING_LITERAL, m.start(), m.end(), Confidence.HIGH, "double_quote")
    for m in re.finditer(r"'([^'\n]{2,})'", text):
        add(m.group(1), AnchorType.STRING_LITERAL, m.start(), m.end(), Confidence.HIGH, "single_quote")
        
    for m in re.finditer(r'File "([^"]+)", line \d+, in (\w+)', text):
        add(m.group(1), AnchorType.FILE_PATH, m.start(1), m.end(1), Confidence.VERY_HIGH, "stack_trace")
        add(m.group(2), AnchorType.IDENTIFIER, m.start(2), m.end(2), Confidence.VERY_HIGH, "stack_trace")
        
    for m in re.finditer(r'(?:raises?|Raises?)\s+([A-Z]\w*(?:Error|Exception|Warning))(?::\s*[\'"]([^\'"]+)[\'"])?', text):
        add(m.group(1), AnchorType.EXCEPTION_NAME, m.start(1), m.end(1), Confidence.VERY_HIGH, "explicit_exception")
        if m.group(2):
            add(m.group(2), AnchorType.ERROR_MESSAGE, m.start(2), m.end(2), Confidence.VERY_HIGH, "explicit_error")
            
    for m in re.finditer(r'\b([a-zA-Z_]\w*)\s*=\s*[\w\'"]+', text):
        add(m.group(1), AnchorType.CONFIG_KEY, m.start(1), m.end(1), Confidence.HIGH, "assignment")
    for m in re.finditer(r'--([a-zA-Z0-9_-]+)', text):
        add(m.group(0), AnchorType.CONFIG_KEY, m.start(0), m.end(0), Confidence.HIGH, "cli_flag")

    words = re.finditer(r'\b[A-Za-z0-9_.\-/\\]+\b', text)
    for m in words:
        w = m.group(0)
        s, e = m.start(), m.end()
        if w.isnumeric() or len(w) < 2:
            continue
            
        if "/" in w or "\\" in w:
            if re.search(r'\.[a-zA-Z0-9]+$', w) or "tests/" in w.lower() or "src/" in w.lower():
                add(w, AnchorType.FILE_PATH, s, e, Confidence.VERY_HIGH, "path_regex")
                continue
        if re.match(r'^[a-zA-Z0-9_-]+\.(py|toml|cfg|ini|txt|md|yml|yaml|json)$', w):
            add(w, AnchorType.FILE_PATH, s, e, Confidence.VERY_HIGH, "filename_regex")
            continue
            
        if "." in w and re.match(r'^[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)+$', w):
            add(w, AnchorType.DOTTED_NAME, s, e, Confidence.HIGH, "dotted_regex")
            continue
            
        if re.match(r'^[A-Z][a-zA-Z0-9]*(?:Error|Exception|Warning)$', w):
            add(w, AnchorType.EXCEPTION_NAME, s, e, Confidence.VERY_HIGH, "exception_regex")
            continue
            
        is_camel = re.match(r'^[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+$', w)
        is_snake = re.match(r'^[a-z]+(?:_[a-z0-9]+)+$', w)
        is_upper = re.match(r'^[A-Z]+(?:_[A-Z0-9]+)+$', w)
        is_dunder = re.match(r'^__\w+__$', w)
        if is_camel or is_snake or is_upper or is_dunder:
            add(w, AnchorType.IDENTIFIER, s, e, Confidence.HIGH, "identifier_regex")
            continue
            
        w_lower = w.lower()
        if w_lower in DOMAIN_TERMS:
            add(w_lower, AnchorType.DOMAIN_TERM, s, e, Confidence.MEDIUM, "domain_term")
        elif w_lower in TEST_CLUES_VOCAB:
            add(w_lower, AnchorType.TEST_CLUE, s, e, Confidence.MEDIUM, "test_clue")
        else:
            for op in OPERATIONS:
                if w_lower == op or w_lower == op + "s" or w_lower == op + "ed" or w_lower == op + "ing":
                    add(op, AnchorType.OPERATION, s, e, Confidence.MEDIUM, "operation_morph")
                    break
                    
    for a in list(anchors):
        if a.confidence in (Confidence.VERY_HIGH, Confidence.HIGH):
            val_lower = a.normalized_value.lower()
            for t in ["redirect", "fragment", "location"]:
                if t in val_lower:
                    add(t, AnchorType.TEST_CLUE, a.source_span[0], a.source_span[1], Confidence.MEDIUM, "derived_test_clue")
    
    seen = {}
    for a in anchors:
        key = (a.normalized_value, a.anchor_type)
        if key not in seen or a.confidence.value > seen[key].confidence.value:
            seen[key] = a
            
    filtered_anchors = list(seen.values())
    filtered_anchors.sort(key=lambda x: (-x.confidence.value, x.source_span[0], x.normalized_value))
    
    limits = {
        AnchorType.IDENTIFIER: 12,
        AnchorType.FILE_PATH: 8,
        AnchorType.STRING_LITERAL: 10,
        AnchorType.OPERATION: 8,
        AnchorType.DOMAIN_TERM: 12,
        AnchorType.TEST_CLUE: 10,
    }
    
    type_counts = {}
    final_anchors = []
    for a in filtered_anchors:
        type_counts[a.anchor_type] = type_counts.get(a.anchor_type, 0) + 1
        if a.anchor_type in limits and type_counts[a.anchor_type] > limits[a.anchor_type]:
            continue
        final_anchors.append(a)
        
    result = SearchAnchors(final_anchors)
    
    if telemetry_logger and run_id and task_id:
        top_anchors = [a.normalized_value for a in final_anchors[:3]]
        payload = {
            "identifier_count": type_counts.get(AnchorType.IDENTIFIER, 0),
            "path_count": type_counts.get(AnchorType.FILE_PATH, 0),
            "literal_count": type_counts.get(AnchorType.STRING_LITERAL, 0),
            "operation_count": type_counts.get(AnchorType.OPERATION, 0),
            "domain_term_count": type_counts.get(AnchorType.DOMAIN_TERM, 0),
            "top_anchors": top_anchors
        }
        telemetry_logger.log_event(run_id, "ANCHORS_EXTRACTED", payload, task_id)
        
    return result
