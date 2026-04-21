from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_baseline, run_variant
from experiments.format_results import view_aggregate_variant_results
from experiments.scenarios.prompt_injection.customer_service_scenario import *

SCENARIO = "customer_service_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_customer_service_contexts()

    variants = {
        "blame_shift": lambda: build_blame_shift_attack(PoisoningScope.SINGLE_INSTANCE),
        "store_credit_only": lambda: build_store_credit_attack(PoisoningScope.SINGLE_INSTANCE),
        "no_apology_policy": lambda: build_no_apology_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    run_baseline(config, SURFACE, SCENARIO, eval_contexts)

    all_variant_results = []

    for variant_name, build_attack in variants.items():
        summary = run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)
        all_variant_results.append(summary)

    view_aggregate_variant_results(all_variant_results, title="Customer Service Single-Instance Aggregate")    

if __name__ == "__main__":
    main()