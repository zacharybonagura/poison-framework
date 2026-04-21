from typing import Any, Dict, Optional, List
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.output_checker import OutputChecker


class MemoryRetrievalAttack(Attack):

    def __init__(
        self,
        name: str,
        success_checker: OutputChecker,
        scope: PoisoningScope = PoisoningScope.PERSISTENT,
        trigger: Optional[str] = None,
        malicious_entries: Optional[List[Dict[str, str]]] = None,
        judge_spec: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name=name or "MemoryRetrievalAttack",
            target=AttackTarget.MEMORY_RETRIEVAL,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger,
            judge_spec=judge_spec,
        )
        self.malicious_entries = malicious_entries

    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        context.setdefault("memory", [])

        for entry in self.malicious_entries:
            context["memory"].append(entry["value"])

        return context

    def persist_longterm(self) -> Optional[List[Dict[str, str]]]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None

        return self.malicious_entries