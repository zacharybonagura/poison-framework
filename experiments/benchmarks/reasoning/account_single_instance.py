from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.reasoning.account_scenario import *

SCENARIO = "account_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    baseline_contexts = (
        build_account_access_reasoning_contexts()
        + build_recent_activity_override_contexts()
        + build_suspicion_bias_contexts()
    )

    variants = {
        "convenience_override": {
            "build_attack": lambda: build_convenience_override_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_account_access_reasoning_contexts(),
        },
        "recent_activity_override": {
            "build_attack": lambda: build_recent_activity_override_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_recent_activity_override_contexts(),
        },
        "suspicion_bias": {
            "build_attack": lambda: build_suspicion_bias_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_suspicion_bias_contexts(),
        },
    }

    run_baseline(config, SURFACE, SCENARIO, baseline_contexts)

    all_variant_results = []

    for variant_name, variant in variants.items():
        summary = run_variant(
            config,
            SURFACE,
            SCENARIO,
            variant_name,
            variant["build_attack"],
            variant["eval_contexts"],
        )
        all_variant_results.append(summary)

    view_aggregate_variant_results(
        all_variant_results,
        title="Account Access Reasoning Single-Instance Aggregate"
    )

if __name__ == "__main__":
    main()