from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.policy_review_scenario import *

SCENARIO = "policy_review_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    eval_contexts = build_policy_review_contexts()

    variants = {
        "exception_suppression": lambda: build_exception_suppression_attack(PoisoningScope.SINGLE_INSTANCE),
        "risk_first": lambda: build_risk_first_attack(PoisoningScope.SINGLE_INSTANCE),
        "deny_on_uncertainty": lambda: build_insufficient_info_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)
    
    view_aggregate_variant_results(all_variant_results, title="Policy Review Single-Instance Aggregate")
    
if __name__ == "__main__":
    main(ExperimentConfig())