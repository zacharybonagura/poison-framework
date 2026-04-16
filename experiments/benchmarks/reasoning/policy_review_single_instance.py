from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_variant
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

    for variant_name, build_attack in variants.items():
        run_variant(
            config,
            SURFACE,
            SCENARIO,
            variant_name,
            build_attack,
            eval_contexts,
        )

if __name__ == "__main__":
    main(ExperimentConfig())