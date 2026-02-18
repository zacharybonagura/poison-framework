from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.success_checker import SuccessChecker

# PromptInjectionAttack represents the attack where we manipulate the instructions
# provided to the agent. By inserting malicious instructions into the prompt, the
# attacker can override or redirect the agent's intended behavior without modifying
# the underlying model or agent logic. 
class PromptInjectionAttack(Attack):

    def __init__(
            self,
            malicious_instruction: str,
            success_checker: SuccessChecker,
            scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
            trigger: Optional[str] = None,
    ):
        super().__init__(
            name="PromptInjectionAttack",
            target=AttackTarget.PROMPT,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger,
        )
        self.malicious_instruction = malicious_instruction
        

    # Insert the malicious instruction into user input if trigger condition is met
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context
        
        original_prompt = context.get("user_input", "")
        poisoned_prompt = original_prompt + "\n" + self.malicious_instruction

        context["user_input"] = poisoned_prompt
        return context
    
    # Return key/value pair to store in long-term memory if persistent attack
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None

        return {
            "source": "prompt_injection",
            "key": self.trigger or "prompt_injection",
            "value": self.malicious_instruction
        }
    