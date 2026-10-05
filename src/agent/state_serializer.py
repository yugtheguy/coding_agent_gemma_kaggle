import json
from dataclasses import asdict
from typing import Dict, Any
from .state import AgentState, Phase, TaskState, RequirementsState, SearchEvidence, FocusedSource, DependencyEvidence, LatestExecution, PatchState
from .debug_ledger import DebugLedger, Hypothesis, NextAction
from .budget_state import BudgetState
from src.infrastructure.io_utils import atomic_write_json

def to_dict(state: AgentState) -> Dict[str, Any]:
    d = asdict(state)
    d["phase"] = state.phase.name
    return d

def from_dict(data: Dict[str, Any]) -> AgentState:
    state = AgentState()
    if "state_version" in data:
        state.state_version = data["state_version"]
    if "phase" in data:
        state.phase = Phase(data["phase"])
    if data.get("task"):
        state.task = TaskState(**data["task"])
    if data.get("requirements"):
        state.requirements = RequirementsState(**data["requirements"])
    if data.get("search_evidence"):
        state.search_evidence = [SearchEvidence(**e) for e in data["search_evidence"]]
    if data.get("focused_source"):
        state.focused_source = [FocusedSource(**s) for s in data["focused_source"]]
    if data.get("dependencies"):
        state.dependencies = [DependencyEvidence(**d) for d in data["dependencies"]]
    if data.get("latest_execution"):
        state.latest_execution = LatestExecution(**data["latest_execution"])
    if data.get("patch"):
        state.patch = PatchState(**data["patch"])
    if data.get("budget"):
        state.budget = BudgetState(**data["budget"])
    if data.get("debug"):
        dbg = data["debug"]
        ledger = DebugLedger(observation=dbg.get("observation", ""), rejected_history_bound=dbg.get("rejected_history_bound", 10))
        if dbg.get("active_hypothesis"):
            ledger.active_hypothesis = Hypothesis(**dbg["active_hypothesis"])
        if dbg.get("rejected_hypotheses"):
            ledger.rejected_hypotheses = [Hypothesis(**h) for h in dbg["rejected_hypotheses"]]
        if dbg.get("next_discriminating_action"):
            ledger.next_discriminating_action = NextAction(**dbg["next_discriminating_action"])
        state.debug = ledger
    return state

def snapshot_state(state: AgentState, path: str):
    from pathlib import Path
    p = Path(path)
    atomic_write_json(p, to_dict(state))

def to_compact_context(state: AgentState) -> str:
    parts = []
    if state.task:
        parts.append(f"TASK:\nID: {state.task.task_id}\n{state.task.issue_text}")
    parts.append(f"REQUIREMENTS:\nMust do: {len(state.requirements.must_do)}\nMust preserve: {len(state.requirements.must_preserve)}")
    
    parts.append("SEARCH EVIDENCE:")
    for e in state.search_evidence[:10]:
        parts.append(f"- [{e.evidence_id}] {e.source_type} ({e.path}): {e.summary}")
    if len(state.search_evidence) > 10:
        parts.append(f"... {len(state.search_evidence) - 10} additional items omitted")
        
    parts.append("FOCUSED SOURCE:")
    for f in state.focused_source[:6]:
        parts.append(f"- {f.path}:{f.line_start}-{f.line_end} ({f.reason})")
    if len(state.focused_source) > 6:
        parts.append(f"... {len(state.focused_source) - 6} additional items omitted")
        
    parts.append("DEPENDENCIES:")
    for d in state.dependencies[:12]:
        parts.append(f"- {d.source} -> {d.target} ({d.relation})")
    if len(state.dependencies) > 12:
        parts.append(f"... {len(state.dependencies) - 12} additional items omitted")
        
    ex = state.latest_execution
    parts.append(f"LATEST EXECUTION:\nCommand: {ex.command}\nCode: {ex.exit_code}\nOutput: {ex.salient_output}")
    
    parts.append(f"DEBUG STATE:\nObservation: {state.debug.observation}")
    if state.debug.active_hypothesis:
        parts.append(f"Active Hypothesis [{state.debug.active_hypothesis.hypothesis_id}]: {state.debug.active_hypothesis.statement}")
    if state.debug.next_discriminating_action:
        na = state.debug.next_discriminating_action
        parts.append(f"Next Action: {na.action_type} on {na.target} (Reason: {na.reason})")
        
    p = state.patch
    parts.append(f"PATCH STATE:\nFiles modified: {len(p.files_modified)}\nAttempts: {p.patch_attempts}")
    
    b = state.budget
    parts.append(f"BUDGET:\nModel turns: {b.model_turns_used}/{b.soft_model_turns}\nElapsed: {b.elapsed_seconds}s/{b.soft_task_seconds}s")
    
    return "\n\n".join(parts)
