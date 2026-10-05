from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NextAction:
    action_type: str
    target: str
    reason: str
    expected_information: str
    cost_class: str

@dataclass
class Hypothesis:
    hypothesis_id: str
    statement: str
    status: str
    supporting_evidence_ids: List[str] = field(default_factory=list)
    disconfirming_evidence_ids: List[str] = field(default_factory=list)
    location: str = ""
    confidence: str = ""
    created_step: int = 0
    updated_step: int = 0

@dataclass
class DebugLedger:
    observation: str = ""
    active_hypothesis: Optional[Hypothesis] = None
    rejected_hypotheses: List[Hypothesis] = field(default_factory=list)
    next_discriminating_action: Optional[NextAction] = None
    rejected_history_bound: int = 10

    def add_hypothesis(self, hypothesis: Hypothesis):
        if self.active_hypothesis:
            self.active_hypothesis.status = "SUPERSEDED"
            self.rejected_hypotheses.append(self.active_hypothesis)
            if len(self.rejected_hypotheses) > self.rejected_history_bound:
                self.rejected_hypotheses.pop(0)
        self.active_hypothesis = hypothesis
        self.active_hypothesis.status = "ACTIVE"
        
    def reject_active_hypothesis(self):
        if self.active_hypothesis:
            self.active_hypothesis.status = "REJECTED"
            self.rejected_hypotheses.append(self.active_hypothesis)
            if len(self.rejected_hypotheses) > self.rejected_history_bound:
                self.rejected_hypotheses.pop(0)
            self.active_hypothesis = None
