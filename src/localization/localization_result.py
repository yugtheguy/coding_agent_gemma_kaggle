from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum, auto

class MatchType(Enum):
    EXACT_PATH = auto()
    PATH_SUFFIX = auto()
    EXACT_SYMBOL = auto()
    EXACT_TEXT = auto()
    ERROR_STRING = auto()
    LITERAL = auto()
    CONFIG_KEY = auto()
    OPERATION = auto()
    DOMAIN_TERM = auto()
    TEST_TERM = auto()

class FileType(Enum):
    SOURCE = auto()
    TEST = auto()
    CONFIG = auto()
    OTHER = auto()

class Confidence(Enum):
    STRONG = auto()
    MODERATE = auto()
    WEAK = auto()

@dataclass
class LocalizationHit:
    path: str
    line: int
    end_line: Optional[int]
    symbol: Optional[str]
    symbol_kind: Optional[str]
    anchor_value: str
    anchor_type: str
    match_type: MatchType
    confidence: str 
    snippet: str = ""
    score: float = 0.0
    provenance: str = ""

@dataclass
class FileCandidate:
    path: str
    score: float
    rank: int
    file_type: FileType
    matched_anchor_ids: List[str]
    evidence_summary: List[str]

@dataclass
class SymbolCandidate:
    qualified_name: str
    path: str
    line_start: int
    line_end: Optional[int]
    symbol_kind: str
    score: float
    matched_anchor_ids: List[str]
    evidence_summary: List[str]

@dataclass
class FocusedRead:
    path: str
    line_start: int
    line_end: int
    reason: str

@dataclass
class LocalizationResult:
    query_anchors: Any
    file_candidates: List[FileCandidate]
    symbol_candidates: List[SymbolCandidate]
    search_backend: str
    stats: Dict[str, Any]
    confidence: Confidence
    focused_reads: List[FocusedRead] = field(default_factory=list)

    def to_search_evidence(self) -> List:
        from src.agent.state import SearchEvidence
        import time
        evidence = []
        # Add top 5 file candidates
        for i, fc in enumerate(self.file_candidates[:5]):
            evidence.append(SearchEvidence(
                evidence_id=f"LOC_FILE_{i+1}",
                source_type="LOCALIZATION_FILE",
                query=", ".join(fc.matched_anchor_ids[:3]),
                path=fc.path,
                score=fc.score,
                summary=f"Rank {fc.rank} {fc.file_type.name} file. Anchors: {', '.join(fc.matched_anchor_ids)}",
                confidence=self.confidence.name,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            ))
            
        # Add top 5 symbol candidates
        for i, sc in enumerate(self.symbol_candidates[:5]):
            evidence.append(SearchEvidence(
                evidence_id=f"LOC_SYM_{i+1}",
                source_type="LOCALIZATION_SYMBOL",
                query=sc.qualified_name,
                path=sc.path,
                symbol=sc.qualified_name,
                line_start=sc.line_start,
                line_end=sc.line_end or 0,
                score=sc.score,
                summary=f"Symbol {sc.qualified_name} ({sc.symbol_kind}). Anchors: {', '.join(sc.matched_anchor_ids)}",
                confidence=self.confidence.name,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            ))
        return evidence
