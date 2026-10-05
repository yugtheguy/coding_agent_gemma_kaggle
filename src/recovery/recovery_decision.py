from dataclasses import dataclass

@dataclass
class RecoveryDecision:
    action: str
    reason: str
    target_phase: str
    requires_new_evidence: bool
    allowed: bool
    cost_class: str
    expected_information: str
    verification_level: int
    stalled: bool
    notes: str
