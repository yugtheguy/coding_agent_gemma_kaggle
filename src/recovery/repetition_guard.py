from dataclasses import dataclass
from typing import List

@dataclass
class ActionSignature:
    action_type: str
    target: str
    query_or_command: str
    phase: str
    evidence_state_hash: str

class RepetitionGuard:
    def __init__(self, max_consecutive_no_info: int = 3):
        self.max_consecutive_no_info = max_consecutive_no_info
        self.history: List[ActionSignature] = []
        self.no_info_count = 0

    def record_action(self, sig: ActionSignature, progress_made: bool):
        self.history.append(sig)
        if not progress_made:
            self.no_info_count += 1
        else:
            self.no_info_count = 0

    def is_action_repeated(self, sig: ActionSignature) -> bool:
        for past in reversed(self.history):
            if past.action_type == sig.action_type and \
               past.target == sig.target and \
               past.query_or_command == sig.query_or_command and \
               past.evidence_state_hash == sig.evidence_state_hash:
                return True
        return False

    def get_block_reason(self, sig: ActionSignature) -> str:
        if self.no_info_count >= self.max_consecutive_no_info:
            return "NO_PROGRESS_DETECTED"
        if self.is_action_repeated(sig):
            return "REPEATED_ACTION_BLOCKED"
        return ""

    def is_blocked(self, sig: ActionSignature) -> bool:
        return bool(self.get_block_reason(sig))
