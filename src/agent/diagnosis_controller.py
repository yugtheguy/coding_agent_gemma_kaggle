import time
from typing import Optional
from src.agent.state import AgentState, Phase
from src.diagnosis.diagnosis_policy import evaluate_diagnosis_readiness
from src.diagnosis.diagnosis_request import DiagnosisRequest
from src.diagnosis.diagnosis_provider import DiagnosisProvider, validate_diagnosis_result
from src.diagnosis.source_acquisition import SourceSnippet
from src.agent.debug_ledger import Hypothesis

class DiagnosisController:
    def __init__(self, provider: DiagnosisProvider, telemetry_logger=None, run_id: str="", task_id: str=""):
        self.provider = provider
        self.telemetry_logger = telemetry_logger
        self.run_id = run_id
        self.task_id = task_id
        
    def run_diagnosis(self, state: AgentState, focused_source: list[SourceSnippet]):
        start = time.time()
        
        state.focused_source = focused_source
        
        readiness = evaluate_diagnosis_readiness(state)
        if readiness != "READY_FOR_DIAGNOSIS":
            return readiness
            
        req = DiagnosisRequest(
            task=state.task,
            requirements=state.requirements,
            top_search_evidence=state.search_evidence[:10],
            focused_source=state.focused_source,
            dependencies=state.dependencies,
            latest_execution=state.latest_execution,
            rejected_hypotheses=[h.__dict__ for h in state.debug.rejected_hypotheses],
            budget_summary=f"Turns left: {state.budget.hard_model_turns}"
        )
        
        if self.telemetry_logger and self.run_id:
            self.telemetry_logger.log_event(self.run_id, "DIAGNOSIS_STARTED", {"readiness": readiness}, self.task_id)
            
        try:
            res = self.provider.diagnose(req)
        except Exception as e:
            if self.telemetry_logger and self.run_id:
                self.telemetry_logger.log_event(self.run_id, "DIAGNOSIS_FAILED", {"error": str(e)}, self.task_id)
            return "DIAGNOSIS_FAILED"
            
        if not validate_diagnosis_result(res):
            if self.telemetry_logger and self.run_id:
                self.telemetry_logger.log_event(self.run_id, "DIAGNOSIS_FAILED", {"error": "validation failed"}, self.task_id)
            return "DIAGNOSIS_FAILED"
            
        if state.debug.active_hypothesis:
            old_h = state.debug.active_hypothesis
            if old_h.statement != res.hypothesis_statement:
                state.reject_hypothesis(self.telemetry_logger, self.run_id)
                
        hid = f"H{len(state.debug.rejected_hypotheses) + 1:03d}"
        loc_str = ""
        if res.root_cause_location:
            loc_str = f"{res.root_cause_location.path}:{res.root_cause_location.line_start}-{res.root_cause_location.line_end}"
            
        new_h = Hypothesis(
            hypothesis_id=hid,
            statement=res.hypothesis_statement,
            status="ACTIVE",
            supporting_evidence_ids=res.supporting_evidence_ids,
            disconfirming_evidence_ids=res.disconfirming_evidence_ids,
            location=loc_str,
            confidence=res.confidence
        )
        
        state.update_hypothesis(new_h, self.telemetry_logger, self.run_id)
        
        duration = (time.time() - start) * 1000
        if self.telemetry_logger and self.run_id:
            self.telemetry_logger.log_event(self.run_id, "DIAGNOSIS_COMPLETED", {
                "hypothesis_id": hid,
                "confidence": res.confidence,
                "root_cause_path": res.root_cause_location.path if res.root_cause_location else None,
                "root_cause_symbol": res.root_cause_location.symbol if res.root_cause_location else None,
                "supporting_evidence_count": len(res.supporting_evidence_ids),
                "disconfirming_evidence_count": len(res.disconfirming_evidence_ids),
                "patch_readiness": res.patch_readiness,
                "next_action_type": res.recommended_action.action_type.name,
                "duration_ms": duration
            }, self.task_id)
            
            self.telemetry_logger.log_event(self.run_id, "NEXT_ACTION_SELECTED", {
                "action_type": res.recommended_action.action_type.name,
                "cost": res.recommended_action.cost.name,
                "target": res.recommended_action.target
            }, self.task_id)
            
        return "SUCCESS"
