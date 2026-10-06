from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.reasoning.refund_scenario import *

SCENARIO = "refund_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    baseline_contexts = (
        build_refund_reasoning_contexts()
        + build_escalate_instead_contexts()
        + build_customer_favor_contexts()
    )

    variants = {
        "default_deny": {
            "build_attack": lambda: build_default_deny_reasoning_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_refund_reasoning_contexts(),
        },
        "escalate_instead": {
            "build_attack": lambda: build_escalate_instead_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_escalate_instead_contexts(),
        },
        "customer_favor": {
            "build_attack": lambda: build_customer_favor_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_customer_favor_contexts(),
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
        title="Refund Reasoning Single-Instance Aggregate"
    )

if __name__ == "__main__":
    main()