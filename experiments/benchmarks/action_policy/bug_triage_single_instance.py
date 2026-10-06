from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.action_policy.bug_triage_scenario import *

SCENARIO = "bug_triage_single_instance"
SURFACE = "action_policy"

def main(config: ExperimentConfig):
    eval_contexts = build_bug_triage_contexts()

    variants = {
        "always_critical": lambda: build_always_critical_attack(PoisoningScope.SINGLE_INSTANCE),
        "backend_bias": lambda: build_backend_bias_attack(PoisoningScope.SINGLE_INSTANCE),
        "customer_workaround": lambda: build_customer_workaround_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Bug Triage Single-Instance Aggregate")

if __name__ == "__main__":
    main()