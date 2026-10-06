from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.multi_attack.autonomous_driving_scenario import *


SCENARIO = "autonomous_driving_single_instance"
SURFACE = "multi_attack"


def main(config: ExperimentConfig):
    eval_contexts = build_autonomous_driving_contexts()

    variants = {
        "prompt_hide_pedestrian_message": lambda: build_hide_pedestrian_message_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "reasoning_unsafe_crosswalk_maneuver": lambda: build_unsafe_crosswalk_maneuver_reasoning_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "tool_traffic_light_overtrust": lambda: build_traffic_light_overtrust_tool_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "memory_false_school_zone_speed": lambda: build_false_school_zone_speed_memory_attack(
            PoisoningScope.SINGLE_INSTANCE
        ),
        "action_policy_override_field": lambda: build_action_policy_override_field_attack(
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
        title="Autonomous Driving Single-Instance Aggregate",
    )


if __name__ == "__main__":
    main()