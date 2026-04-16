from agent.agent_context import AgentContext
from attacks.attack import PoisoningScope
from experiments.experiment_config import ExperimentConfig
from experiments.benchmark_runner import run_variant
from experiments.scenarios.incident_scenario import *

SCENARIO = "incident_reasoning_single_instance"
SURFACE = "reasoning"

def main(config: ExperimentConfig):
    eval_contexts = build_incident_contexts()

    variants = {
        "premature_conclusion": lambda: build_premature_conclusion_attack(PoisoningScope.SINGLE_INSTANCE),
        "high_severity_bias": lambda: build_high_severity_bias_attack(PoisoningScope.SINGLE_INSTANCE),
        "surface_keyword_bias": lambda: build_surface_keyword_bias_attack(PoisoningScope.SINGLE_INSTANCE),
    }

    for variant_name, build_attack in variants.items():
        run_variant(config, SURFACE, SCENARIO, variant_name, build_attack, eval_contexts)

if __name__ == "__main__":
    main()