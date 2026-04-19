from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.extraction_scenario import *

SCENARIO = "extraction_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_extraction_contexts()

    variants = {
        "urgent_priority": lambda: build_urgent_priority_attack(PoisoningScope.SINGLE_INSTANCE),
        "escalate_immediately": lambda: build_escalate_immediately_attack(PoisoningScope.SINGLE_INSTANCE),
        "case_id_omission": lambda: build_case_id_omission_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Extraction Single-Instance Aggregate")

if __name__ == "__main__":
    main()