from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from attacks.prompt_injection import PromptInjectionAttack
from experiments.experiment_config import ExperimentConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.format_results import view_results
from attacks.output_checker import *
from experiments.benchmark_runner import run_variant
from experiments.scenarios.email_scenario import *

SCENARIO = "email_single_instance"
SURFACE = "prompt_injection"

def main(config: ExperimentConfig):
    eval_contexts = build_email_contexts()

    variants = {
        "omg_style": lambda: build_omg_attack(PoisoningScope.SINGLE_INSTANCE),
        "magical_signature": lambda: build_magical_attack(PoisoningScope.SINGLE_INSTANCE),
        "bullet_format": lambda: build_bullet_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    for variant_name, build_attack in variants.items():
        run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)

if __name__ == "__main__":
    main()
