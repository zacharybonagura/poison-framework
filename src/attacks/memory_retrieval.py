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

            malicious_memory: str = "",
            num_entries: int = 1,
            memory_key: str = "retrieval_bias",
            override_mode = None,
            override_k = None,
            override_key = None,
            
    ):
        super().__init__(
            name=name or "MemoryRetrievalAttack",
            target=AttackTarget.MEMORY_RETRIEVAL,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger
        )

        self.malicious_memory = malicious_memory
        self.num_entries = num_entries
        self.memory_key = memory_key
        self.override_mode = override_mode
        self.override_k = override_k
        self.override_key = override_key

    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        
        if not self.should_trigger(context):
            return context
        
        context.setdefault("memory", [])

        # Allow multiple entries to influence flooding and retrieval probability
        for _ in range(self.num_entries):
            context["memory"].append(self.malicious_memory)
        
        return context

    def modify_retrieval(self, mode, k, key):
        if self.override_mode is not None:
            mode = self.override_mode
        if self.override_k is not None:
            k = self.override_k
        if self.override_key is not None:
            key = self.override_key
        return mode, k, key
    
    # Return key/value pair to store in long-term memory if persistent attack
    def persist_longterm(self) -> Optional[List]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None

        entries = []

        for _ in range(self.num_entries):
            entries.append({
                "source": "memory_retrieval_persistent",
                "key": self.memory_key,
                "value": self.malicious_memory
            })
        
        return entries