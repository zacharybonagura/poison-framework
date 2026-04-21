from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.reasoning.task_scheduling_scenario import *

SCENARIO = "task_scheduling_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    baseline_contexts = (
        build_task_scheduling_reasoning_contexts()
        + build_easy_task_bias_contexts()
        + build_dependency_assumption_contexts()
    )

    variants = {
        "big_project_bias": {
            "build_attack": lambda: build_big_project_bias_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_task_scheduling_reasoning_contexts(),
        },
        "easy_task_bias": {
            "build_attack": lambda: build_easy_task_bias_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_easy_task_bias_contexts(),
        },
        "dependency_assumption": {
            "build_attack": lambda: build_dependency_assumption_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_dependency_assumption_contexts(),
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
        title="Task Scheduling Reasoning Single-Instance Aggregate"
    )

if __name__ == "__main__":
    main()