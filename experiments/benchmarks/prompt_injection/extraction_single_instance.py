from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from attacks.prompt_injection import PromptInjectionAttack
from experiments.experiment_config import ExperimentConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.format_results import view_results
from attacks.output_checker import *
from experiments.benchmark_runner import run_variant
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

    for variant_name, build_attack in variants.items():
        run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)

if __name__ == "__main__":
    main()