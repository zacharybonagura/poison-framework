from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.tool_interface.transit_scenario import *

SCENARIO = "transit_single_instance"
SURFACE = "tool_interface"


def main(config: ExperimentConfig):
    baseline_contexts = (
        build_status_contexts()
        + build_delay_contexts()
        + build_schedule_contexts()
    )

    variants = {
        "status_as_delay": {
            "build_attack": lambda: build_status_as_delay_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_status_contexts(),
        },
        "delay_as_status": {
            "build_attack": lambda: build_delay_as_status_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_delay_contexts(),
        },
        "status_as_schedule": {
            "build_attack": lambda: build_status_as_schedule_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_status_contexts(),
        },
        "schedule_as_status": {
            "build_attack": lambda: build_schedule_as_status_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_schedule_contexts(),
        },
        "delay_as_schedule": {
            "build_attack": lambda: build_delay_as_schedule_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_delay_contexts(),
        },
        "schedule_as_delay": {
            "build_attack": lambda: build_schedule_as_delay_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_schedule_contexts(),
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
        title="Transit Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()