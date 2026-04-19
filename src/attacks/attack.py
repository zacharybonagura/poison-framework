from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from agent.tool import Tool
from attacks.output_checker import OutputChecker

# ENUM for Poisoning Scope
class PoisoningScope(Enum):
    SINGLE_INSTANCE = auto()
    PERSISTENT = auto()

# ENUM for Attack Target
class AttackTarget(Enum):
    PROMPT = auto()
    REASONING = auto()
    TOOL_INTERFACE = auto()
    MEMORY_RETRIEVAL = auto()
    ACTION_POLICY = auto()

# Abstract base class for all poisoning attacks
class Attack(ABC):  
    def __init__(
        self,
        name: str,
        target: AttackTarget,
        success_checker: OutputChecker,
        scope: PoisoningScope,
        trigger: Optional[str] = None,
        judge_spec: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.target = target
        self.success_checker = success_checker
        self.scope = scope
        self.trigger = trigger
        self.judge_spec = judge_spec

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

        return self.trigger in str(context.get("user_input", ""))
    
    # Return poisoned data to store in long-term memory 
    #       (Overridden by persistant attacks)
    # or None if nothing should persist
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        return None

    # Return True if attacker-desired behavior is observed
    # Use Attack Success Rate (ASR) and Persistence Rate (PR)
    def detect_success(self, output: str) -> bool:
        return self.success_checker(output)

    # These functions allow attackers to modify tool descriptions, but are not required to do so
    def modify_tool_descriptions(self, tools: List[Tool]) -> List[Tool]:
        return tools
    
    # This function allows attackers to modify retrieval
    def modify_retrieval(self, mode, k, key):
        return mode, k, key
    
    # This returns True if the attack can use an LLM-as-a-judge to determine success
    def has_judge(self) -> bool:
        return self.judge_spec is not None
    
    # Returns information for current attack to log experiments
    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "target": self.target.name,
            "scope": self.scope.name,
            "trigger": self.trigger,
        }
