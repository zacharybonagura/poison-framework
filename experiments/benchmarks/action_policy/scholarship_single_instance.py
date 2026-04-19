from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.scholarship_scenario import *

SCENARIO = "scholarship_single_instance"
SURFACE = "action_policy"

def main(config: ExperimentConfig):
    eval_contexts = build_scholarship_contexts()

    variants = {
        "merit_only": lambda: build_merit_only_attack(PoisoningScope.SINGLE_INSTANCE),
        "need_only": lambda: build_need_only_attack(PoisoningScope.SINGLE_INSTANCE),
        "strict_rejection": lambda: build_strict_rejection_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Scholarship Single-Instance Aggregate")

if __name__ == "__main__":
    main()