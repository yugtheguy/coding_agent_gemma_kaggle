from dataclasses import dataclass

@dataclass
class PatchProposal:
    path: str
    target_symbol: str
    edit_type: str # REPLACE, INSERT, DELETE, CREATE_FILE
    old_text: str
    new_text: str
    reason_summary: str
    expected_invariant_restored: str
    expected_behavior_change: str
    risk_notes: str
