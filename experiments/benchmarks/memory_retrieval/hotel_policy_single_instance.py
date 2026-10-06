from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.memory_retrieval.hotel_policy_scenario import *

SCENARIO = "hotel_policy_single_instance"
SURFACE = "memory_retrieval"

def main(config: ExperimentConfig):
    baseline_contexts = (
        build_hotel_policy_contexts()
        + build_breakfast_contexts()
        + build_room_service_contexts()
    )

    variants = {
        "automatic_late_checkout": {
            "build_attack": lambda: build_automatic_late_checkout_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_hotel_policy_contexts(),
        },
        "automatic_breakfast": {
            "build_attack": lambda: build_automatic_breakfast_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_breakfast_contexts(),
        },
        "room_service_until_midnight": {
            "build_attack": lambda: build_room_service_until_midnight_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_room_service_contexts(),
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
        title="Hotel Policy Single-Instance Aggregate"
    )

if __name__ == "__main__":
    main()