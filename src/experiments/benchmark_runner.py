from experiments.experiment_config import ExperimentConfig
from experiments.experiment_runner import ExperimentRunner
from experiments.format_results import view_results

def run_baseline(base_config, surface, scenario, eval_contexts, seed_memory=None):
    print(f"\n\n===== Running baseline =====")

    config = ExperimentConfig(
        retrieval_mode=base_config.retrieval_mode,
        retrieval_k=base_config.retrieval_k,
        retrieval_key=base_config.retrieval_key,
        mode=base_config.mode,
        num_trials=1,
        memory_path=f"experiments/memory/{surface}/{scenario}_baseline.json",
        results_path=f"experiments/results/{surface}/{scenario}_baseline.jsonl",
        judge_mode=base_config.judge_mode,
        judge_model=base_config.judge_model,
        task_judge_strategy=base_config.task_judge_strategy,
        attack_judge_strategy=base_config.attack_judge_strategy,
    )

    runner = ExperimentRunner(config)
    runner.reset_memory()
    runner.reset_results()

    if seed_memory is not None:
        seed_memory(config.memory_path)

    results = runner.run(None, eval_contexts, lambda: [])
    print(results)
    summary = view_results(config.results_path)

    return {
        "variant_name": "baseline",
        "surface": surface,
        "scenario": scenario,
        "results": results,
        "results_path": config.results_path,
        "summary": summary,
    }


def run_variant(base_config, surface, scenario, variant_name, build_attack, eval_contexts,
                attack_context=None, seed_memory=None):
    print(f"\n\n===== Running variant: {variant_name} =====")

    config = ExperimentConfig(
        retrieval_mode=base_config.retrieval_mode,
        retrieval_k=base_config.retrieval_k,
        retrieval_key=base_config.retrieval_key,
        mode=base_config.mode,
        num_trials=base_config.num_trials,
        memory_path=f"experiments/memory/{surface}/{scenario}_{variant_name}.json",
        results_path=f"experiments/results/{surface}/{scenario}_{variant_name}.jsonl",
        judge_mode=base_config.judge_mode,
        judge_model=base_config.judge_model,
        task_judge_strategy=base_config.task_judge_strategy,
        attack_judge_strategy=base_config.attack_judge_strategy,
    )

    runner = ExperimentRunner(config)
    runner.reset_memory()
    runner.reset_results()

    if seed_memory is not None:
        seed_memory(config.memory_path)

    results = runner.run(attack_context, eval_contexts, build_attack)

    print(results)
    summary = view_results(config.results_path)

    return {
        "variant_name": variant_name,
        "surface": surface,
        "scenario": scenario,
        "results": results,
        "results_path": config.results_path,
        "summary": summary,
    }