from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.moderation_scenario import *

SCENARIO = "moderation_single_instance"
SURFACE = "action_policy"

def main(config: ExperimentConfig):
    eval_contexts = build_moderation_contexts()

    variants = {
        "under_enforcement": lambda: build_under_enforcement_attack(PoisoningScope.SINGLE_INSTANCE),
        "always_escalate": lambda: build_always_escalate_attack(PoisoningScope.SINGLE_INSTANCE),
        "engagement_over_safety": lambda: build_engagement_over_safety_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Moderation Single-Instance Aggregate")

if __name__ == "__main__":
    main()