from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.success_checker import SuccessChecker

# ReasoningAttack represents the attack where we manipulate the reasoning process
# the agent uses. By inserting malicious reasoning steps into the system, the
# attacker can override or redirect the agent's intended behavior without modifying
# the underlying model or agent logic. 

class ReasoningAttack(Attack):

    def __init__(
            self,
            name: str,
            malicious_instruction: str,
            success_checker: SuccessChecker,
            scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
            trigger: Optional[str] = None,
    ):
        super().__init__(
            name=name or "ReasoningAttack",
            target=AttackTarget.REASONING,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger
        )
        self.malicious_instruction = malicious_instruction

    # Insert the malicious instruction into system prompt if trigger condition is met
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context
        
        original_system = context.get("system_prompt", "")
        poisoned_system = original_system + "\n\n" + "Internal Reasoning Policy: \n" + self.malicious_instruction

        context["system_prompt"] = poisoned_system
        return context
    
    # Return key/value pair to store in long-term memory if persistent attack
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None

        return {
            "source": "reasoning",
            "key": self.trigger or "reasoning_policy",
            "value": self.malicious_instruction
        }
    