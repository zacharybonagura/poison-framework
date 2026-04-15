from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from attacks.prompt_injection import PromptInjectionAttack
from experiments.experiment_config import ExperimentConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.format_results import view_results
from attacks.output_checker import *
from experiments.benchmark_runner import run_variant
from experiments.scenarios.customer_service_scenario import *

SCENARIO = "customer_service_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_customer_service_contexts()

    variants = {
        "blame_shift": lambda: build_blame_shift_attack(PoisoningScope.SINGLE_INSTANCE),
        "store_credit_only": lambda: build_store_credit_attack(PoisoningScope.SINGLE_INSTANCE),
        "all_caps": lambda: build_all_caps_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    for variant_name, build_attack in variants.items():
        run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)

if __name__ == "__main__":
    main()