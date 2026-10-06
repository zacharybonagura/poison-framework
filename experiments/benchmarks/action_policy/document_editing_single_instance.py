from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.action_policy.document_editing_scenario import *

SCENARIO = "document_editing_single_instance"
SURFACE = "action_policy"


def main(config: ExperimentConfig):
    baseline_contexts = build_document_editing_contexts()

    variants = {
        "add_justification": {
            "build_attack": lambda: build_add_justification_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_document_editing_contexts(),
        },
        "before_after": {
            "build_attack": lambda: build_before_after_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_document_editing_contexts(),
        },
        "aggressive_tone": {
            "build_attack": lambda: build_aggressive_tone_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_document_editing_contexts(),
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
        title="Document Editing Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()