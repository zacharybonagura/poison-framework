from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.multi_attack.airport_screening_scenario import *


SCENARIO = "airport_screening_pairwise_single_instance"
SURFACE = "multi_attack"


def main(config: ExperimentConfig):
    eval_contexts = build_airport_screening_contexts()

    variants = {
        variant_name: (
            lambda pair_builder=pair_builder: pair_builder(PoisoningScope.SINGLE_INSTANCE)
        )
        for variant_name, pair_builder in AIRPORT_SCREENING_PAIRWISE_ATTACKS.items()
    }

    run_baseline(
        base_config=config,
        surface=SURFACE,
        scenario=SCENARIO,
        eval_contexts=eval_contexts,
    )

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        print(f"\n===== Running pairwise variant: {variant_name} =====")

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
        title="Airport Screening Pairwise Single-Instance Aggregate",
    )


if __name__ == "__main__":
    main()