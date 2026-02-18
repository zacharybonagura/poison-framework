import json
import os
from typing import Optional, Callable, Dict, Any

from experiments.experiment_config import ExperimentConfig
from agent.agent_runner import AgentRunner
from agent.agent_context import AgentContext
from attacks.attack import Attack, PoisoningScope

# ExperimentRunner orchestrates attack experiments and evaluation.
class ExperimentRunner:

    def __init__(self, config: ExperimentConfig):
        self.config = config

        # set up directories
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

    # Evaluate a list of contexts under a given attack setting
    # Each evaluation row is logged to the results JSONL file.
    def _evaluate(self, trial_id: Optional[int], agent: AgentRunner, eval_contexts: list[AgentContext], 
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

                # Inject into agent context if single instance
                if attack is not None and attack.scope == PoisoningScope.SINGLE_INSTANCE: 
                    did_trigger, eval_ctx = self.agent.inject_attack_into_prompt(eval_ctx, attack=attack)

                output = agent.run(eval_ctx, attack=attack)

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
                }
                if trial_id is not None: row["trial_id"] = trial_id

                if attack is not None and attack.scope == PoisoningScope.SINGLE_INSTANCE:
                    row["triggered"] = "Yes" if did_trigger else "No"
                    row["attack"] = attack.metadata()
                    
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


    # Executes an experiment. 
    # If no attack is provided, run baseline once
    # If attack is provided, run num_trials.
    # If attack is single_instance, do not inject into memory,
    #          - inject in agent context
    #          - evaluate ASR using current agent
    # If attack is persistent, inject into memory before evaluation, 
    #          - evaluate ASR using current agent
    #          - evlauate PR using fresh agent
    def run(self, attack_context: Optional[AgentContext],
            eval_contexts: list[AgentContext], 
            build_attack: Callable[[], Optional[Attack]]) -> Dict[str, Any]:

        attack = build_attack()

        # Baseline attack
        if attack is None:
            self.reset_memory()
            self.reset_results()

            stats = self._evaluate(
                trial_id=None,
                agent=self.agent,
                eval_contexts=eval_contexts,
                attack=None,
                eval_type="baseline"
            )

            return {
                "ASR_mean": 0.0,
                "PR_mean": None,
                "memory_path": self.config.memory_path,
                "output_path": self.config.output_path,
            }
        
        num_trials = self.config.num_trials
        all_asr = []
        all_pr = []

        # Evaluate Attack
        for trial_id in range(num_trials):
            attack = build_attack()

            self.reset_memory()

            if attack_context is not None and attack is not None and attack.scope:
                inject_context = AgentContext(
                    label=attack_context.label,
                    system_prompt=attack_context.system_prompt,
                    memory=list(attack_context.memory) if attack_context.memory else [],
                    user_input=attack_context.user_input
                )

                # Inject into memory if not single instance
                if attack.scope != PoisoningScope.SINGLE_INSTANCE:
                    attack_info = self.agent.inject_attack_into_memory(inject_context, attack=attack)

                    with open(self.config.output_path, "a", encoding="utf-8") as f:
                        row = {
                            "trial_id": trial_id,
                            "eval_type": "memory_inject",
                            "label": attack_context.label,
                            "info": attack_info,
                        }
                        f.write(json.dumps(row) + "\n")

            asr_stats = self._evaluate(
                trial_id=trial_id,
                agent=self.agent,
                eval_contexts=eval_contexts,
                attack=attack,
                eval_type="asr"
            )
            asr = asr_stats["success_rate"]
            all_asr.append(asr)

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
                    trial_id=trial_id,
                    agent=fresh_agent,
                    eval_contexts=eval_contexts,
                    attack=attack,
                    eval_type="pr"
                )

                persistence_rate = persistence_stats["success_rate"]
                all_pr.append(persistence_rate)

        mean_asr = sum(all_asr) / len(all_asr) if all_asr else 0.0
        mean_pr = sum(all_pr) / len(all_pr) if all_pr else None

        return {
            "eval_count": asr_stats["eval_count"],
            "success_count": asr_stats["success_count"],
            "ASR_mean": mean_asr,
            "PR_mean": mean_pr,
            "memory_path": self.config.memory_path,
            "output_path": self.config.output_path
        }
