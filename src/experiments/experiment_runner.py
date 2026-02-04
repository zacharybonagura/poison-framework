import json
import os
from typing import Optional, Callable, Dict, Any

from experiments.experiment_config import ExperimentConfig
from agent.agent_runner import AgentRunner
from agent.agent_context import AgentContext
from attacks.attack import Attack, PoisoningScope

class ExperimentRunner:

    def __init__(self, config: ExperimentConfig):
        self.config = config

        os.makedirs(os.path.dirname(self.config.memory_path),exist_ok=True)
        os.makedirs(os.path.dirname(self.config.output_path), exist_ok=True)

        self.agent = AgentRunner(
            memory_path=self.config.memory_path,
            retrieval_mode=self.config.retrieval_mode,
            retrieval_k=self.config.retrieval_k,
            retrieval_key=self.config.retrieval_key,
            llm_mode=self.config.mode,
        )
    
    def reset_memory(self) -> None:
        self.agent.persistent_memory.reset_poison()

    def reset_results(self) -> None:
         open(self.config.output_path, "w", encoding="utf-8").close()

    def _evaluate(self, agent: AgentRunner, eval_contexts: list[AgentContext], 
                  attack: Optional[Attack], eval_type: str) -> Dict[str, Any]:
        success_count = 0
        eval_count = len(eval_contexts)

        with open(self.config.output_path, "a", encoding="utf-8") as f:
            for i, eval_context in enumerate(eval_contexts):
                eval_ctx = AgentContext(
                    label=eval_context.label,
                    system_prompt=eval_context.system_prompt,
                    user_input=eval_context.user_input,
                    memory=list(eval_context.memory or [])
                )
                output = agent.run(eval_ctx)

                success = False
                if attack is not None: 
                    success = attack.detect_success(output)
                    if success: success_count += 1

                row = {
                    "eval_type": eval_type,
                    "label": eval_context.label,
                    "success": "Passed" if success else "Failed",
                    "eval_index": i,
                    "output": output,
                    "config": self.config.to_dict()
                }
                f.write(json.dumps(row) + "\n")

        if eval_count > 0:
            success_rate = success_count / eval_count
        else:
            success_rate = 0.0
        
        return {
            "eval_count": eval_count,
            "success_count": success_count,
            "success_rate": success_rate
        }


    def run(self, attack_context: Optional[AgentContext],
            eval_contexts: list[AgentContext], 
            build_attack: Callable[[], Optional[Attack]]) -> Dict[str, Any]:

        attack = build_attack()

        if attack_context is not None and attack is not None:
            inject_context = AgentContext(
                label=attack_context.label,
                system_prompt=attack_context.system_prompt,
                memory=list(attack_context.memory) if attack_context.memory else [],
                user_input=attack_context.user_input
            )

            attack_info = self.agent.inject_attack(inject_context, attack=attack)

            with open(self.config.output_path, "a", encoding="utf-8") as f:
                row = {
                    "eval_type": "attack",
                    "label": attack_context.label,
                    "info": attack_info,
                    "config": self.config.to_dict()
                }
                f.write(json.dumps(row) + "\n")

        asr_stats = self._evaluate(
            agent=self.agent,
            eval_contexts=eval_contexts,
            attack=attack,
            eval_type="baseline" if attack is None else "asr"
        )
        asr = asr_stats["success_rate"]

        persistence_rate = None
        if attack is not None and attack.scope == PoisoningScope.PERSISTENT:
            fresh_agent = AgentRunner(
                memory_path=self.config.memory_path,
                retrieval_mode=self.config.retrieval_mode,
                retrieval_k=self.config.retrieval_k,
                retrieval_key=self.config.retrieval_key,
                llm_mode=self.config.mode,
            )

            persistence_stats = self._evaluate(
                agent=fresh_agent,
                eval_contexts=eval_contexts,
                attack=attack,
                eval_type="pr"
            )

            persistence_rate = persistence_stats["success_rate"]

        return {
            "eval_count": asr_stats["eval_count"],
            "success_count": asr_stats["success_count"],
            "ASR": asr,
            "PR": persistence_rate,
            "memory_path": self.config.memory_path,
            "output_path": self.config.output_path
        }
