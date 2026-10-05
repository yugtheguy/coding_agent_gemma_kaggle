from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

class AnchorType(Enum):
    IDENTIFIER = auto()
    FILE_PATH = auto()
    MODULE_PATH = auto()
    DOTTED_NAME = auto()
    BACKTICKED_TERM = auto()
    STRING_LITERAL = auto()
    ERROR_MESSAGE = auto()
    EXCEPTION_NAME = auto()
    CONFIG_KEY = auto()
    OPERATION = auto()
    DOMAIN_TERM = auto()
    TEST_CLUE = auto()
    RAW_TERM = auto()

class Confidence(Enum):
    VERY_HIGH = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

@dataclass
class Anchor:
    value: str
    anchor_type: AnchorType
    source_span: Tuple[int, int]
    normalized_value: str
    confidence: Confidence
    provenance: str = ""

    def __hash__(self):
        return hash((self.normalized_value, self.anchor_type.name))
        
    def __eq__(self, other):
        if not isinstance(other, Anchor):
            return False
        return self.normalized_value == other.normalized_value and self.anchor_type == other.anchor_type

@dataclass
class SearchAnchors:
    anchors: List[Anchor] = field(default_factory=list)

    def to_search_plan(self) -> str:
        primary_exact = []
        secondary_exact = []
        concept_terms = []
        test_terms = []
        
        seen = set()
        
        for a in self.anchors:
            if a.normalized_value in seen:
                continue
                
            if a.confidence == Confidence.VERY_HIGH:
                primary_exact.append(a.normalized_value)
                seen.add(a.normalized_value)
            elif a.confidence == Confidence.HIGH:
                secondary_exact.append(a.normalized_value)
                seen.add(a.normalized_value)
            elif a.anchor_type in (AnchorType.OPERATION, AnchorType.DOMAIN_TERM):
                concept_terms.append(a.normalized_value)
                seen.add(a.normalized_value)
            elif a.anchor_type == AnchorType.TEST_CLUE:
                test_terms.append(a.normalized_value)
                seen.add(a.normalized_value)
                
        lines = []
        if primary_exact:
            lines.append("PRIMARY EXACT:")
            for i, val in enumerate(primary_exact, 1):
                lines.append(f"{i}. {val}")
        if secondary_exact:
            lines.append("SECONDARY EXACT:")
            for i, val in enumerate(secondary_exact, 1):
                lines.append(f"{i}. {val}")
        if concept_terms:
            lines.append("CONCEPT TERMS:")
            for i, val in enumerate(concept_terms, 1):
                lines.append(f"{i}. {val}")
        if test_terms:
            lines.append("TEST TERMS:")
            for i, val in enumerate(test_terms, 1):
                lines.append(f"{i}. {val}")
                
        return "\n\n".join(lines)

    def to_search_evidence(self) -> List:
        from src.agent.state import SearchEvidence
        evidence = []
        for i, a in enumerate(self.anchors, 1):
            evidence.append(SearchEvidence(
                evidence_id=f"ANC_{i:03d}",
                source_type=a.anchor_type.name,
                query=a.normalized_value,
                summary=f"Extracted from {a.provenance} (Confidence: {a.confidence.name})"
            ))
        return evidence
