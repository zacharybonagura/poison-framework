from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.success_checker import SuccessChecker

class PlanningAttack(Attack):

    def __init__(
        self,
        name: str,
        malicious_policy: str,
        success_checker: SuccessChecker,
        scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
        trigger: Optional[str] = None
    ):
        super().__init__(
            name=name or "PlanningAttack",
            target=AttackTarget.PLANNING,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger
        )
        self.malicious_policy = malicious_policy

    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        original_system = context.get("system_prompt", "")

        poisoned_system = (
            original_system
            + "\n\nAction Planning Policy:\n"
            + self.malicious_policy
        )

        context["system_prompt"] = poisoned_system
        return context

    def persist_longterm(self):
        if self.scope != PoisoningScope.PERSISTENT:
            return None
        
        return {
            "source": "planning",
            "key": self.trigger or "planning_policy",
            "value": self.malicious_policy
        }