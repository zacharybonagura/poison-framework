from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.output_checker import OutputChecker

# PromptInjectionAttack represents the attack where we manipulate the instructions
# provided to the agent. By inserting malicious instructions into the prompt, the
# attacker can override or redirect the agent's intended behavior without modifying
# the underlying model or agent logic. 
class PromptInjectionAttack(Attack):

    def __init__(
            self,
            name: str,
            malicious_instruction: str,
            success_checker: OutputChecker,
            scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
            trigger: Optional[str] = None,
            judge_spec: Optional[Dict[str, Any]] = None,
            position: str = "suffix",
            separator: str = "\n",
    ):
        super().__init__(
            name=name or "PromptInjectionAttack",
            target=AttackTarget.PROMPT,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger,
            judge_spec=judge_spec
        )
        self.malicious_instruction = malicious_instruction
        self.position = position
        self.separator = separator

    def _insert_by_position(self, original_prompt:str) -> str:
        instruction = self.malicious_instruction
        sep = self.separator

        if self.position == "suffix":
            return original_prompt + sep + instruction
        
        if self.position == "prefix":
            return instruction + sep + original_prompt
        
        # Trigger-relative insertion only makes sense if a trigger exists
        if self.position in {"before_trigger", "after_trigger", "replace_trigger"}:
            if not self.trigger:
                return original_prompt + sep + instruction
            
            idx = original_prompt.find(self.trigger)
            if idx == -1:
                return original_prompt + sep + instruction
            
            if self.position == "before_trigger":
                return (
                    original_prompt[:idx]
                    + instruction
                    + sep
                    + original_prompt[idx:]
                )

            if self.position == "after_trigger":
                trigger_end = idx + len(self.trigger)
                return (
                    original_prompt[:trigger_end]
                    + sep
                    + instruction
                    + original_prompt[trigger_end:]
                )

            if self.position == "replace_trigger":
                return original_prompt.replace(
                    self.trigger,
                    instruction,
                    1
                )
            
        raise ValueError(
            f"Unknown prompt injection position: {self.position}. "
            "Expected one of: suffix, prefix, before_trigger, after_trigger, replace_trigger."
        )
            
    # Insert the malicious instruction into user input if trigger condition is met
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        original_prompt = context.get("user_input", "")
        context["user_input"] = self._insert_by_position(original_prompt)
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
    