from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.finance_scenario import *

SCENARIO = "finance_single_instance"
SURFACE = "tool_interface"


def main(config: ExperimentConfig):
    baseline_contexts = (
        build_price_contexts()
        + build_news_contexts()
        + build_profile_contexts()
    )

    variants = {
        "price_as_news": {
            "build_attack": lambda: build_price_as_news_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_price_contexts(),
        },
        "news_as_price": {
            "build_attack": lambda: build_news_as_price_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_news_contexts(),
        },
        "price_as_profile": {
            "build_attack": lambda: build_price_as_profile_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_price_contexts(),
        },
        "profile_as_price": {
            "build_attack": lambda: build_profile_as_price_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_profile_contexts(),
        },
        "news_as_profile": {
            "build_attack": lambda: build_news_as_profile_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_news_contexts(),
        },
        "profile_as_news": {
            "build_attack": lambda: build_profile_as_news_attack(PoisoningScope.SINGLE_INSTANCE),
            "eval_contexts": build_profile_contexts(),
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
        title="Finance Single-Instance Aggregate"
    )


if __name__ == "__main__":
    main()