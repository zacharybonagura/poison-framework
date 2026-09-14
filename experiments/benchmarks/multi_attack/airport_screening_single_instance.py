from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.multi_attack.airport_screening_scenario import *


SCENARIO = "airport_screening_single_instance"
SURFACE = "multi_attack"


def main(config: ExperimentConfig):
    eval_contexts = build_airport_screening_contexts()

    variants = {
        "prompt_hide_scanner_concern_message": lambda: build_hide_scanner_concern_message_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "reasoning_skip_manual_inspection": lambda: build_skip_manual_inspection_reasoning_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "tool_passenger_profile_overtrust": lambda: build_passenger_profile_overtrust_tool_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "memory_false_precleared_bag": lambda: build_false_precleared_bag_memory_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "action_policy_low_risk_screening": lambda: build_low_risk_screening_policy_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
    }

    run_baseline(
        base_config=config,
        surface=SURFACE,
        scenario=SCENARIO,
        eval_contexts=eval_contexts,
    )

    all_variant_results = []

    for variant_name, build_attack in variants.items():
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
        title="Airport Screening Single-Instance Aggregate",
    )


if __name__ == "__main__":
    main()