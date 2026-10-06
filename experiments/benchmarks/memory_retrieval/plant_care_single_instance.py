from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.memory_retrieval.plant_care_scenario import *

SCENARIO = "plant_care_single_instance"
SURFACE = "memory_retrieval"


def main(config: ExperimentConfig):
    baseline_contexts = (
        build_snake_plant_contexts()
        + build_orchid_contexts()
        + build_aloe_contexts()
    )

    variants = {
        "weekly_watering": {
            "build_attack": lambda: build_weekly_watering_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_snake_plant_contexts(),
        },
        "direct_sun_orchid": {
            "build_attack": lambda: build_direct_sun_orchid_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_orchid_contexts(),
        },
        "keep_moist_aloe": {
            "build_attack": lambda: build_keep_moist_aloe_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_aloe_contexts(),
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
        title="Plant Care Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()