from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .debug_ledger import DebugLedger
from .budget_state import BudgetState

class Phase(Enum):
    UNDERSTAND = "UNDERSTAND"
    LOCALIZE = "LOCALIZE"
    DIAGNOSE = "DIAGNOSE"
    REPRODUCE = "REPRODUCE"
    PATCH = "PATCH"
    VERIFY_TARGET = "VERIFY_TARGET"
    VERIFY_REGRESSION = "VERIFY_REGRESSION"
    FINAL_CHECK = "FINAL_CHECK"
    SUBMIT = "SUBMIT"
    DONE = "DONE"
    ABANDONED = "ABANDONED"

@dataclass
class TaskState:
    task_id: str
    issue_text: str
    hints: str = ""
    repository: str = ""
    base_revision: str = ""

@dataclass
class RequirementsState:
    must_do: List[str] = field(default_factory=list)
    must_preserve: List[str] = field(default_factory=list)
    ambiguities: List[str] = field(default_factory=list)

@dataclass
class SearchEvidence:
    evidence_id: str
    source_type: str
    query: str
    path: str = ""
    symbol: str = ""
    line_start: int = 0
    line_end: int = 0
    score: float = 0.0
    summary: str = ""
    confidence: str = ""
    timestamp: str = ""

@dataclass
class FocusedSource:
    path: str
    symbol: str = ""
    line_start: int = 0
    line_end: int = 0
    reason: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    content_digest: str = ""

@dataclass
class DependencyEvidence:
    source: str
    target: str
    relation: str
    raw_relation: str = ""
    evidence_id: str = ""

@dataclass
class LatestExecution:
    command: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    result_type: str = ""
    salient_output: str = ""
    traceback_summary: str = ""
    test_count: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    timed_out: bool = False
    truncated: bool = False

@dataclass
class PatchState:
    files_modified: List[str] = field(default_factory=list)
    edit_count: int = 0
    patch_attempts: int = 0
    target_test_status: str = "NONE"
    regression_test_status: str = "NONE"
    syntax_status: str = "NONE"
    diff_check_status: str = "NONE"
    patch_nonempty: bool = False
    last_patch_summary: str = ""

@dataclass
class AgentState:
    state_version: int = 1
    phase: Phase = Phase.UNDERSTAND
    task: Optional[TaskState] = None
    requirements: RequirementsState = field(default_factory=RequirementsState)
    search_evidence: List[SearchEvidence] = field(default_factory=list)
    focused_source: List[FocusedSource] = field(default_factory=list)
    dependencies: List[DependencyEvidence] = field(default_factory=list)
    latest_execution: LatestExecution = field(default_factory=LatestExecution)
    debug: DebugLedger = field(default_factory=DebugLedger)
    patch: PatchState = field(default_factory=PatchState)
    budget: BudgetState = field(default_factory=BudgetState)

    def transition_to(self, new_phase: Phase, telemetry_logger=None, run_id: str=""):
        allowed = {
            Phase.UNDERSTAND: [Phase.LOCALIZE, Phase.ABANDONED],
            Phase.LOCALIZE: [Phase.DIAGNOSE, Phase.ABANDONED],
            Phase.DIAGNOSE: [Phase.REPRODUCE, Phase.PATCH, Phase.ABANDONED],
            Phase.REPRODUCE: [Phase.DIAGNOSE, Phase.PATCH, Phase.ABANDONED],
            Phase.PATCH: [Phase.VERIFY_TARGET, Phase.ABANDONED],
            Phase.VERIFY_TARGET: [Phase.PATCH, Phase.VERIFY_REGRESSION, Phase.ABANDONED],
            Phase.VERIFY_REGRESSION: [Phase.PATCH, Phase.FINAL_CHECK, Phase.ABANDONED],
            Phase.FINAL_CHECK: [Phase.SUBMIT, Phase.ABANDONED],
            Phase.SUBMIT: [Phase.DONE, Phase.ABANDONED],
            Phase.DONE: [],
            Phase.ABANDONED: [],
        }
        if new_phase not in allowed[self.phase]:
            raise ValueError(f"Invalid transition from {self.phase.name} to {new_phase.name}")
        old_phase = self.phase
        self.phase = new_phase
        if telemetry_logger and run_id:
            telemetry_logger.log_event(run_id, "PHASE_CHANGED", {"from": old_phase.name, "to": new_phase.name})

    def update_hypothesis(self, hypothesis, telemetry_logger=None, run_id: str=""):
        old_id = self.debug.active_hypothesis.hypothesis_id if self.debug.active_hypothesis else None
        self.debug.add_hypothesis(hypothesis)
        if telemetry_logger and run_id:
            telemetry_logger.log_event(run_id, "HYPOTHESIS_UPDATED", {
                "previous_hypothesis_id": old_id,
                "new_hypothesis_id": hypothesis.hypothesis_id
            })

    def reject_hypothesis(self, telemetry_logger=None, run_id: str=""):
        if not self.debug.active_hypothesis:
            return
        h_id = self.debug.active_hypothesis.hypothesis_id
        ev_ids = self.debug.active_hypothesis.disconfirming_evidence_ids
        self.debug.reject_active_hypothesis()
        if telemetry_logger and run_id:
            telemetry_logger.log_event(run_id, "HYPOTHESIS_REJECTED", {
                "hypothesis_id": h_id,
                "evidence_ids": ev_ids
            })
