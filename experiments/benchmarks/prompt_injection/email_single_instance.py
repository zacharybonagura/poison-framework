from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.prompt_injection.email_scenario import *

SCENARIO = "email_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_email_contexts()

    variants = {
        "demanding_tone": lambda: build_demanding_tone_attack(PoisoningScope.SINGLE_INSTANCE),
        "no_actual_ask": lambda: build_no_actual_ask_attack(PoisoningScope.SINGLE_INSTANCE),
        "false_urgency": lambda: build_false_urgency_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Email Single-Instance Aggregate")

if __name__ == "__main__":
    main()