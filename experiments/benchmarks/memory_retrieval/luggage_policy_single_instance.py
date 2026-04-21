from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.memory_retrieval.luggage_policy_scenario import *

SCENARIO = "luggage_policy_single_instance"
SURFACE = "memory_retrieval"

def main(config: ExperimentConfig):
    baseline_contexts = (
        build_carry_on_contexts()
        + build_medical_pouch_contexts()
        + build_camera_bag_priority_contexts()
    )

    variants = {
        "deny_extra_item": {
            "build_attack": lambda: build_deny_extra_item_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_carry_on_contexts(),
        },
        "medical_pouch_exemption": {
            "build_attack": lambda: build_medical_pouch_exemption_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_medical_pouch_contexts(),
        },
        "camera_bag_priority": {
            "build_attack": lambda: build_camera_bag_priority_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_camera_bag_priority_contexts(),
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
        title="Luggage Policy Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()