from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.multi_attack.autonomous_driving_scenario import *


SCENARIO = "autonomous_driving_full_sweep_single_instance"
SURFACE = "multi_attack"


def main(config: ExperimentConfig):

    eval_contexts = build_autonomous_driving_contexts()

    variants = {
        "full_sweep": lambda: build_full_sweep_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(
        base_config=config,
        surface=SURFACE,
        scenario=SCENARIO,
        eval_contexts=eval_contexts,
    )

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        print(f"\n===== Running full-sweep variant: {variant_name} =====")

        summary = run_variant(
            base_config=config,
            surface=SURFACE,
            scenario=SCENARIO,
            variant_name=variant_name,
            build_attack=build_attack,
            eval_contexts=eval_contexts,
        )

        all_variant_results.append(summary)

    view_aggregate_variant_results(
        all_variant_results,
        title="Autonomous Driving Full-Sweep Single-Instance Aggregate",
    )


if __name__ == "__main__":
    main()