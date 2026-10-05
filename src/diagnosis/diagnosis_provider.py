import json
from .diagnosis_request import DiagnosisRequest
from .diagnosis_result import DiagnosisResult, RootCauseLocation
from .action_selection import NextAction, ActionType, ActionCost

DIAGNOSIS_PROMPT_VERSION = "e00_diag_v1"

class DiagnosisProvider:
    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        raise NotImplementedError

class MockDiagnosisProvider(DiagnosisProvider):
    def __init__(self, mock_result: DiagnosisResult):
        self.mock_result = mock_result
        self.last_request = None
        
    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        self.last_request = request
        return self.mock_result

class HarnessDiagnosisProvider(DiagnosisProvider):
    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        raise RuntimeError("HarnessDiagnosisProvider not yet bound to official Kaggle runtime.")

def validate_diagnosis_result(res: DiagnosisResult) -> bool:
    if not res.hypothesis_statement:
        return False
    if res.confidence not in ("HIGH", "MEDIUM", "LOW"):
        return False
    if res.patch_readiness not in ("READY", "NEEDS_EVIDENCE", "NOT_LOCALIZED"):
        return False
    if not isinstance(res.recommended_action, NextAction):
        return False
    if res.recommended_action.cost not in (ActionCost.CHEAP, ActionCost.MEDIUM, ActionCost.EXPENSIVE):
        return False
    return True
