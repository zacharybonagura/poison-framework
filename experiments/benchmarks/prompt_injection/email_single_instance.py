from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_variant
from experiments.scenarios.email_scenario import *

SCENARIO = "email_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_email_contexts()

    variants = {
        "demanding_tone": lambda: build_demanding_tone_attack(PoisoningScope.SINGLE_INSTANCE),
        "no_actual_ask": lambda: build_no_actual_ask_attack(PoisoningScope.SINGLE_INSTANCE),
        "false_urgency": lambda: build_false_urgency_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    for variant_name, build_attack in variants.items():
        run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)

if __name__ == "__main__":
    main()