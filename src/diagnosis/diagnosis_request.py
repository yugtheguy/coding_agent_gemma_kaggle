from dataclasses import dataclass
from typing import List, Dict, Any
from src.agent.state import TaskState, RequirementsState, SearchEvidence, DependencyEvidence, LatestExecution
from .source_acquisition import SourceSnippet

@dataclass
class DiagnosisRequest:
    task: TaskState
    requirements: RequirementsState
    top_search_evidence: List[SearchEvidence]
    focused_source: List[SourceSnippet]
    dependencies: List[DependencyEvidence]
    latest_execution: LatestExecution
    rejected_hypotheses: List[Dict[str, Any]]
    budget_summary: str
