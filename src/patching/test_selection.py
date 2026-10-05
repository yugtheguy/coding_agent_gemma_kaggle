from dataclasses import dataclass
from typing import List, Optional

@dataclass
class VerificationTarget:
    command: str
    target_type: str # EXISTING_TEST, REPRODUCER, SYNTAX, CUSTOM_COMMAND
    reason: str
    expected_signal: str
    cost_class: str # CHEAP, MEDIUM, EXPENSIVE
