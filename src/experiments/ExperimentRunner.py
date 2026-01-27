import json
import os
from typing import Optional, Callable, Dict, Any

from experiments.ExperimentConfig import ExperimentConfig
from agent.AgentRunner import AgentRunner
from agent.AgentContext import AgentContext
from attacks.Attack import Attack

class ExperimentRunner:

    def __init__(self, config: ExperimentConfig):
        self.config = config

        os.makedirs(os.path.dirname(self.config.memory_path),exist_ok=True)
        os.makedirs(os.path.dirname(self.config.output_path), exist_ok=True)
        open(self.config.output_path, "w", encoding="utf-8").close()

        self.agent = AgentRunner(
            memory_path=self.config.memory_path,
            retrieval_mode=self.config.retrieval_mode,
            retrieval_k=self.config.retrieval_k,
            retrieval_key=self.config.retrieval_key,
            llm_mode="fake"
        )
    
    def reset_memory(self) -> None:
        self.agent.persistent_memory.save([])

    def run(self, label:str, base_context: AgentContext, build_attack: Callable[[], Optional[Attack]]) -> Dict[str, Any]:
        did_trigger_count = 0
        success_count = 0
        #longterm_persisted_count = 0

        with open(self.config.output_path, "a", encoding="utf-8") as f:
            for r in range(self.config.rounds):
                    attack = build_attack()

                    context = AgentContext(
                        system_prompt=base_context.system_prompt,
                        memory=list(base_context.memory) if base_context.memory else [],
                        user_input=base_context.user_input
                    )

                    output, info = self.agent.run(context, attack=attack)

                    did_trigger = bool(info.get("did_trigger", False))
                    success = bool(info.get("success",False))
                    #longterm_persisted = info.get("longterm_persisted") is not None

                    if did_trigger: did_trigger_count += 1
                    if success: success_count += 1
                    #if longterm_persisted: longterm_persisted_count += 1

                    attack_name = None
                    if info.get("attack"): attack_name = info["attack"].get("name")

                    row = {
                        "label": label,
                        "output": output,
                        "info": info,
                        # "round": r,
                        "config": self.config.to_dict(),
                    }
                    f.write(json.dumps(row) + "\n")

        asr = (success_count / did_trigger_count) if did_trigger_count else 0.0
        #longterm_pr = (longterm_persisted_count / did_trigger_count) if did_trigger_count else 0.0

        return {
            "rounds": self.config.rounds,
            "did_trigger": did_trigger_count,
            "successes": success_count,
            #"longterm_persisted": longterm_persisted_count,
            "ASR": asr,
            #"LongtermPersistenceRate": longterm_pr,
            "retrieval_mode": self.config.retrieval_mode,
            "retrieval_k": self.config.retrieval_k,
            "retrieval_key": self.config.retrieval_key,
            "memory_path": self.config.memory_path,
            "output_path": self.config.output_path
        }