from dataclasses import dataclass
from typing import List, Optional
from src.agent.state import TaskState, RequirementsState, LatestExecution
from src.diagnosis.source_acquisition import SourceSnippet
from src.agent.debug_ledger import Hypothesis

@dataclass
class PatchRequest:
    task: TaskState
    requirements: RequirementsState
    root_cause_location: str
    invariant: str
    focused_source: List[SourceSnippet]
    active_hypothesis: Hypothesis
    supporting_evidence: List[str]
    disconfirming_evidence: List[str]
    latest_execution: LatestExecution
    patch_attempt_number: int
    budget_summary: str
