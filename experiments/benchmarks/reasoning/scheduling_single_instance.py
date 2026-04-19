from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.scheduling_scenario import *

SCENARIO = "scheduling_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    eval_contexts = build_scheduling_contexts()

    variants = {
        "midday_comfort_bias": lambda: build_convenience_first_attack(PoisoningScope.SINGLE_INSTANCE),
        "in_hours_priority": lambda: build_working_hours_overweight_attack(PoisoningScope.SINGLE_INSTANCE),
        "earliest_workable_slot": lambda: build_earliest_slot_bias_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Scheduling Single-Instance Aggregate")

if __name__ == "__main__":
    main(ExperimentConfig())