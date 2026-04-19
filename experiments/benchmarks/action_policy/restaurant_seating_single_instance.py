from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.restaurant_seating_scenario import *

SCENARIO = "restaurant_seating_single_instance"
SURFACE = "action_policy"

def main(config: ExperimentConfig):
    eval_contexts = build_restaurant_seating_contexts()

    variants = {
        "largest_party_first": lambda: build_largest_party_first_attack(PoisoningScope.SINGLE_INSTANCE),
        "newest_party_first": lambda: build_newest_party_first_attack(PoisoningScope.SINGLE_INSTANCE),
        "walkin_over_reservation": lambda: build_walkin_over_reservation_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Restaurant Seating Single-Instance Aggregate")

if __name__ == "__main__":
    main()