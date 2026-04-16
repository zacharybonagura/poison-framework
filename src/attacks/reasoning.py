from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.output_checker import OutputChecker

# ReasoningAttack represents the attack where we manipulate the reasoning process
# the agent uses. By inserting malicious reasoning steps into the system, the
# attacker can override or redirect the agent's intended behavior without modifying
# the underlying model or agent logic. 

class ReasoningAttack(Attack):

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
            name=name or "ReasoningAttack",
            target=AttackTarget.REASONING,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger,
            judge_spec=judge_spec,
        )
        self.malicious_instruction = malicious_instruction
        self.position = position
        self.separator = separator

    def _insert_by_position(self, original_text: str) -> str:
        instruction = "Internal Reasoning Policy:\n" + self.malicious_instruction
        sep = self.separator

        if self.position == "suffix":
            return original_text + sep + instruction

        if self.position == "prefix":
            return instruction + sep + original_text

        if self.position in {"before_trigger", "after_trigger", "replace_trigger"}:
            if not self.trigger:
                return original_text + sep + instruction

            idx = original_text.find(self.trigger)
            if idx == -1:
                return original_text + sep + instruction

            if self.position == "before_trigger":
                return (
                    original_text[:idx]
                    + instruction
                    + sep
                    + original_text[idx:]
                )

            if self.position == "after_trigger":
                trigger_end = idx + len(self.trigger)
                return (
                    original_text[:trigger_end]
                    + sep
                    + instruction
                    + original_text[trigger_end:]
                )

            if self.position == "replace_trigger":
                return original_text.replace(self.trigger, instruction, 1)

        raise ValueError(
            f"Unknown reasoning insertion position: {self.position}. "
            "Expected one of: suffix, prefix, before_trigger, after_trigger, replace_trigger."
        )
    
    # Insert the malicious instruction into system prompt if trigger condition is met
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        original_system = context.get("system_prompt", "")
        context["system_prompt"] = self._insert_by_position(original_system)
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
    