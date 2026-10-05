from enum import Enum
from dataclasses import dataclass

class ActionCost(Enum):
    CHEAP = "CHEAP"
    MEDIUM = "MEDIUM"
    EXPENSIVE = "EXPENSIVE"

class ActionType(Enum):
    READ = "READ"
    RUN = "RUN"
    TEST = "TEST"
    GRAPH = "GRAPH"
    SEARCH = "SEARCH"
    PATCH = "PATCH"

@dataclass
class NextAction:
    action_type: ActionType
    cost: ActionCost
    description: str
    target: str = ""
