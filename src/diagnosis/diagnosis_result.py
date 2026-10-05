from dataclasses import dataclass, field
from typing import List, Optional
from .action_selection import NextAction

@dataclass
class RootCauseLocation:
    path: str
    symbol: str = ""
    line_start: int = 0
    line_end: int = 0

@dataclass
class DiagnosisResult:
    observation: str
    hypothesis_statement: str
    supporting_evidence_ids: List[str]
    disconfirming_evidence_ids: List[str]
    root_cause_location: Optional[RootCauseLocation]
    invariant: str
    confidence: str 
    recommended_action: NextAction
    patch_readiness: str 
    uncertainties: str = ""
    evaluation_label: str = "UNKNOWN" 
