from experiments.experiment_config import ExperimentConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.format_results import view_results

def run_variant(base_config, surface, scenario, variant_name, build_attack, eval_contexts, attack_context=None):
    print(f"\n\n===== Running variant: {variant_name} =====")

    config = ExperimentConfig(
        retrieval_mode=base_config.retrieval_mode,
        retrieval_k=base_config.retrieval_k,
        retrieval_key=base_config.retrieval_key,
        mode=base_config.mode,
        num_trials=base_config.num_trials,
        memory_path=f"experiments/memory/{surface}/{scenario}_{variant_name}.json",
        results_path=f"experiments/results/{surface}/{scenario}_{variant_name}.jsonl",
    )

    runner = ExperimentRunner(config)
    runner.reset_memory()
    runner.reset_results()

    runner.run(None, eval_contexts, lambda: [])
    results = runner.run(attack_context, eval_contexts, build_attack)

    print(results)
    view_results(config.results_path)