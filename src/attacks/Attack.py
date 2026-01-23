from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Optional

# ENUM for Poisoning Scope
class PoisoningScope(Enum):
    SESSION = auto()
    PERSISTENT = auto()

# ENUM for Attack Target
class AttackTarget(Enum):
    PROMPT = auto()
    REASONING = auto()
    TOOL_INTERFACE = auto()
    GOAL = auto()
    MEMORY_RETRIEVAL = auto()

# Abstract base class for all poisoning attacks
class Attack(ABC):  
    def __init__(
        self,
        name: str,
        target: AttackTarget,
        scope: PoisoningScope,
        trigger: Optional[str] = None,
    ):
        self.name = name
        self.target = target
        self.scope = scope
        self.trigger = trigger

    # Inject poisoning into the agent context before execution
    # This is the only method allowed to modify context
    @abstractmethod
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # Determine whether the attack activates for this run
    # Attack active always if no trigger passed, or only active with trigger
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        if self.trigger is None:
            return True

        return self.trigger in str(context)

    def persist_session(self) -> Optional[str]:
        return None
    
    # Return poisoned data to store in long-term memory 
    #       (Overridden by persistant attacks)
    # or None if nothing should persist
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        return None

    # Return True if attacker-desired behavior is observed
    # Use Attack Success Rate (ASR) and Persistence Rate (PR)
    @abstractmethod
    def detect_success(self, output: str) -> bool:
        pass

    # Returns information for current attack to log experiments
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "target": self.target.name,
            "scope": self.scope.name,
            "trigger": self.trigger,
        }
