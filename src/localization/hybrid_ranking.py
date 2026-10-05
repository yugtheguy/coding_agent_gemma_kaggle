import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .localization_result import LocalizationResult, FileCandidate, SymbolCandidate, Confidence as LexicalConfidence
from .query_expansion import QueryExpansion
from .semantic_backend import SemanticHit

@dataclass
class HybridLocalizationResult(LocalizationResult):
    semantic_used: bool = False
    semantic_usefulness: str = "UNHELPFUL"
    semantic_calls_used: int = 0
    query_expansion: Optional[QueryExpansion] = None
    semantic_query: str = ""
    hybrid_stats: Dict[str, Any] = None

    def to_search_evidence(self) -> List:
        from src.agent.state import SearchEvidence
        import time
        evidence = super().to_search_evidence()
        if self.semantic_used and self.query_expansion:
            evidence.append(SearchEvidence(
                evidence_id="SEMANTIC_QUERY",
                source_type="SEMANTIC",
                query=self.semantic_query,
                path="",
                score=0.0,
                summary=f"Usefulness: {self.semantic_usefulness}. Expanded concepts: {', '.join(self.query_expansion.implementation_concepts)}",
                confidence=self.confidence.name,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            ))
        return evidence

def build_semantic_query(lexical_result: LocalizationResult, expansion: QueryExpansion, max_terms: int = 12) -> str:
    terms = []
    
    for a in lexical_result.query_anchors.anchors:
        if a.confidence.name in ("VERY_HIGH", "HIGH"):
            if a.normalized_value not in terms:
                terms.append(a.normalized_value)
                
    for c in expansion.implementation_concepts:
        if c not in terms:
            terms.append(c)
            
    for t in expansion.test_terms + expansion.alternative_symbols:
        if t not in terms:
            terms.append(t)
            
    return " ".join(terms[:max_terms])

def assess_semantic_usefulness(semantic_hits: List[SemanticHit], lexical_result: LocalizationResult) -> str:
    if not semantic_hits:
        return "UNHELPFUL"
        
    valid_hits = [h for h in semantic_hits if not h.path.startswith("tests/") and h.path.endswith(".py")]
    if not valid_hits:
        return "UNHELPFUL"
        
    paths = set(h.path for h in semantic_hits)
    if len(paths) == 1 and len(semantic_hits) > 1:
        return "MIXED"
        
    return "USEFUL"

def run_hybrid_ranking(
    lexical_result: LocalizationResult,
    semantic_hits: List[SemanticHit],
    expansion: QueryExpansion,
    semantic_query: str,
    semantic_calls_used: int = 1,
    telemetry_logger = None,
    run_id: str = "",
    task_id: str = ""
) -> HybridLocalizationResult:
    start_time = time.time()
    
    usefulness = assess_semantic_usefulness(semantic_hits, lexical_result)
    
    file_map = {fc.path: fc for fc in lexical_result.file_candidates}
    sem_points = [30.0, 20.0, 15.0, 10.0, 5.0, 3.0]
    
    for i, hit in enumerate(semantic_hits):
        points = sem_points[i] if i < len(sem_points) else 1.0
        
        if hit.path in file_map:
            fc = file_map[hit.path]
            fc.score += points
            fc.evidence_summary.append(f"SEMANTIC: rank {hit.raw_rank}")
        else:
            from .localization_result import FileType
            ftype = FileType.TEST if "test" in hit.path.lower() else FileType.SOURCE
            fc = FileCandidate(
                path=hit.path,
                score=points,
                rank=0,
                file_type=ftype,
                matched_anchor_ids=[],
                evidence_summary=[f"SEMANTIC: rank {hit.raw_rank}"]
            )
            file_map[hit.path] = fc
            
    all_files = list(file_map.values())
    all_files.sort(key=lambda x: (-x.score, x.path))
    for i, fc in enumerate(all_files):
        fc.rank = i + 1
        
    new_confidence = lexical_result.confidence
    if all_files:
        top_score = all_files[0].score
        if top_score >= 120.0:
            new_confidence = LexicalConfidence.STRONG
        elif top_score >= 40.0:
            new_confidence = LexicalConfidence.MODERATE
        else:
            new_confidence = LexicalConfidence.WEAK
            
    sym_map = {sc.qualified_name: sc for sc in lexical_result.symbol_candidates}
    for i, hit in enumerate(semantic_hits):
        points = sem_points[i] if i < len(sem_points) else 1.0
        if hit.symbol:
            if hit.symbol in sym_map:
                sc = sym_map[hit.symbol]
                sc.score += points
                sc.evidence_summary.append(f"SEMANTIC: rank {hit.raw_rank}")
            else:
                from .localization_result import SymbolCandidate
                sc = SymbolCandidate(
                    qualified_name=hit.symbol,
                    path=hit.path,
                    line_start=hit.line_start or 1,
                    line_end=hit.line_end,
                    symbol_kind="UNKNOWN",
                    score=points,
                    matched_anchor_ids=[],
                    evidence_summary=[f"SEMANTIC: rank {hit.raw_rank}"]
                )
                sym_map[hit.symbol] = sc
                
    all_syms = list(sym_map.values())
    all_syms.sort(key=lambda x: (-x.score, x.path, x.qualified_name))
    
    duration = (time.time() - start_time) * 1000
    stats = dict(lexical_result.stats)
    stats["hybrid_duration_ms"] = duration
    
    hr = HybridLocalizationResult(
        query_anchors=lexical_result.query_anchors,
        file_candidates=all_files[:10],
        symbol_candidates=all_syms[:10],
        search_backend=lexical_result.search_backend,
        stats=stats,
        confidence=new_confidence,
        focused_reads=list(lexical_result.focused_reads),
        semantic_used=True,
        semantic_usefulness=usefulness,
        semantic_calls_used=semantic_calls_used,
        query_expansion=expansion,
        semantic_query=semantic_query,
        hybrid_stats={"duration": duration}
    )
    
    if usefulness == "USEFUL" and semantic_hits:
        from .localization_result import FocusedRead
        top_hit = semantic_hits[0]
        if top_hit.line_start is not None:
            hr.focused_reads.insert(0, FocusedRead(
                path=top_hit.path,
                line_start=max(1, top_hit.line_start - 5),
                line_end=top_hit.line_end + 5 if top_hit.line_end else top_hit.line_start + 20,
                reason=f"Semantic match top hit"
            ))
            
    if telemetry_logger and run_id and task_id:
        telemetry_logger.log_event(run_id, "HYBRID_LOCALIZATION_COMPLETED", {
            "lexical_confidence": lexical_result.confidence.name,
            "semantic_used": True,
            "semantic_usefulness": usefulness,
            "final_confidence": hr.confidence.name,
            "top_files": [fc.path for fc in hr.file_candidates[:2]],
            "semantic_calls_used": semantic_calls_used
        }, task_id)
        
    return hr
