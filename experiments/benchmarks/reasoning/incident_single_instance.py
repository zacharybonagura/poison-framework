from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.incident_scenario import *

SCENARIO = "incident_reasoning_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    eval_contexts = build_incident_contexts()

    variants = {
        "early_clue_anchoring": lambda: build_early_clue_anchoring_attack(PoisoningScope.SINGLE_INSTANCE),
        "template_routing": lambda: build_template_routing_attack(PoisoningScope.SINGLE_INSTANCE),
        "severity_escalation": lambda: build_severity_escalation_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Incident Single-Instance Aggregate")

if __name__ == "__main__":
    main()