from typing import Any, Dict, Optional
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.output_checker import OutputChecker
import json 

class ActionPolicyAttack(Attack):

    def __init__(
        self,
        name: str,
        malicious_policy: str,
        success_checker: OutputChecker,
        scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
        trigger: Optional[str] = None
    ):
        super().__init__(
            name=name or "ActionPolicyAttack",
            target=AttackTarget.ACTION_POLICY,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger
        )
        self.malicious_policy = malicious_policy

    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        context.setdefault("plan", [])
        context["plan"].append(self.malicious_policy)

        return context

    def persist_longterm(self):
        if self.scope != PoisoningScope.PERSISTENT:
            return None
        
        return {
            "source": "planning",
            "key": self.trigger or "planning_policy",
            "value": "Action Planning Policy:\n" + self.malicious_policy
        }