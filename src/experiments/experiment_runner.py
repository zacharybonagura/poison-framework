import json
import os
from typing import Optional, Callable, Dict, Any, List

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
                  attacks: Optional[List[Attack]], eval_type: str, apply_active_injection: bool = True) -> Dict[str, Any]:
        success_count = 0
        eval_count = len(eval_contexts)

        with open(self.config.output_path, "a", encoding="utf-8") as f:
            for i, eval_context in enumerate(eval_contexts):
                eval_ctx = AgentContext(
                    label=eval_context.label,
                    system_prompt=eval_context.system_prompt,
                    user_input=eval_context.user_input,
                    tools=list(eval_context.tools or []),
                    memory=list(eval_context.memory or []),
                    plan=list(eval_context.plan or [])
                )

                # Inject attacks into agent context
                triggered_attacks, eval_ctx = [], eval_ctx

                if attacks and apply_active_injection:
                    triggered_attacks, eval_ctx = agent.inject_active_attacks(
                        eval_ctx,
                        attacks=attacks
                    )

                triggered_names = {a["name"] for a in triggered_attacks}

                output = agent.run(eval_ctx, attacks=attacks)

                attack_success = {}

                if attacks:
                    scored_attacks = attacks or []

                    if eval_type == "pr":
                        scored_attacks = [a for a in scored_attacks if a.scope == PoisoningScope.PERSISTENT]

                    for attack in scored_attacks:
                        attack_success[attack.name] = attack.detect_success(output)

                overall_success = all(attack_success.values()) if attack_success else False
                
                if overall_success: success_count += 1

                attack_info = []

                if attacks:
                    displayed_attacks = attacks

                    if eval_type == "pr":
                        displayed_attacks = [a for a in attacks if a.scope == PoisoningScope.PERSISTENT]

                    for a in displayed_attacks:
                        meta = a.metadata()

                        attack_info.append({
                            "name": meta["name"],
                            "target": meta["target"],
                            "scope": meta["scope"],
                            "triggered": meta["name"] in triggered_names,
                            "success": attack_success.get(meta["name"], False)
                        })

                row = {
                    "eval_type": eval_type,
                    "label": eval_context.label,
                    "attacks": attack_info,
                    "success": "Passed" if overall_success else "Failed",
                    "eval_index": i,
                    "output": output,
                }

                if trial_id is not None: row["trial_id"] = trial_id
                    
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
    # If attack is persistent,
    #          - inject into context, evaluate PR, 
    #          - evaluate ASR using current agent
    #          - then inject into memory
    #          - evlauate PR using fresh agent
    def run(self, attack_context: Optional[AgentContext],
            eval_contexts: list[AgentContext], 
            build_attacks: Callable[[], Optional[List[Attack]]]) -> Dict[str, Any]:

        attacks = build_attacks()

        # Baseline attack
        if attacks is None or len(attacks) == 0:
            self.reset_memory()
            self.reset_results()

            _ = self._evaluate(
                trial_id=None,
                agent=self.agent,
                eval_contexts=eval_contexts,
                attacks=None,
                eval_type="baseline",
                apply_active_injection=False
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

        for trial_id in range(num_trials):
            attacks = build_attacks()
            self.reset_memory()

            has_persistent_attack = any(a.scope == PoisoningScope.PERSISTENT for a in attacks)

            # 1. ASR: active injection in current session
            asr_stats = self._evaluate(
                trial_id=trial_id,
                agent=self.agent,
                eval_contexts=eval_contexts,
                attacks=attacks,
                eval_type="asr",
                apply_active_injection=True
            )
            all_asr.append(asr_stats["success_rate"])

            # 2. Persist after ASR if needed
            if has_persistent_attack and attack_context is not None:
                inject_context = AgentContext(
                    label=attack_context.label,
                    system_prompt=attack_context.system_prompt,
                    user_input=attack_context.user_input,
                    tools=list(attack_context.tools or []),
                    memory=list(attack_context.memory or []),
                    plan=list(attack_context.plan or []),
                )

                triggered, _ = self.agent.inject_attacks_into_memory(
                    inject_context,
                    attacks=attacks
                )

                with open(self.config.output_path, "a", encoding="utf-8") as f:
                    row = {
                        "trial_id": trial_id,
                        "eval_type": "memory_inject",
                        "label": attack_context.label,
                        "attack_info": triggered,
                    }
                    f.write(json.dumps(row) + "\n")

                # 3. PR: fresh session, no active injection, only poisoned memory
                fresh_agent = AgentRunner(
                    memory_path=self.config.memory_path,
                    retrieval_mode=self.config.retrieval_mode,
                    retrieval_k=self.config.retrieval_k,
                    retrieval_key=self.config.retrieval_key,
                    llm_mode=self.config.mode,
                )

                pr_stats = self._evaluate(
                    trial_id=trial_id,
                    agent=fresh_agent,
                    eval_contexts=eval_contexts,
                    attacks=attacks,
                    eval_type="pr",
                    apply_active_injection=False
                )
                all_pr.append(pr_stats["success_rate"])

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
