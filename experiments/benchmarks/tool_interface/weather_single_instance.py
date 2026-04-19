from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.weather_scenario import *

SCENARIO = "weather_single_instance"
SURFACE = "tool_interface"


def main(config: ExperimentConfig):
    baseline_contexts = (
        build_current_weather_contexts()
        + build_alert_contexts()
        + build_climate_contexts()
    )

    variants = {
        "current_as_alert": {
            "build_attack": lambda: build_current_as_alert_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_current_weather_contexts(),
        },
        "alert_as_current": {
            "build_attack": lambda: build_alert_as_current_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_alert_contexts(),
        },
        "current_as_climate": {
            "build_attack": lambda: build_current_as_climate_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_current_weather_contexts(),
        },
        "climate_as_current": {
            "build_attack": lambda: build_climate_as_current_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_climate_contexts(),
        },
        "alert_as_climate": {
            "build_attack": lambda: build_alert_as_climate_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_alert_contexts(),
        },
        "climate_as_alert": {
            "build_attack": lambda: build_climate_as_alert_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_climate_contexts(),
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
        title="Weather Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()