import argparse
import importlib.util
import os
import sys
from src.experiments.experiment_config import ExperimentConfig

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def load_experiment(attack_type: str, experiment_name: str):
    path = os.path.join("experiments","benchmarks",attack_type,f"{experiment_name}.py")

    if not os.path.exists(path):
        raise ValueError(f"Experiment not found: {path}")

    spec = importlib.util.spec_from_file_location("experiment",path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "main"):
        raise ValueError(f"{path} does not define main(config)")
    
    return module.main

def run_experiment(args):
    main_fn = load_experiment(args.attack, args.experiment)
    
    memory_path = (
        args.memory_path
        if args.memory_path is not None
        else f"experiments/memory/{args.attack}/{args.experiment}.json"
    )

    output_path = (
        args.output_path
        if args.output_path is not None
        else f"experiments/results/{args.attack}/{args.experiment}.jsonl"
    )

    config = ExperimentConfig(
            retrieval_mode=args.retrieval_mode,
            retrieval_k=args.retrieval_k,
            retrieval_key=args.retrieval_key,
            mode=args.llm,
            memory_path=memory_path,
            output_path=output_path,
    )

    print("\n=== Running Experiment ===")
    print(f"attack: {args.attack}")
    print(f"experiment: {args.experiment}")
    print(f"llm: {args.llm}")
    print(f"retrieval_mode: {args.retrieval_mode}")
    print(f"retrieval_k: {args.retrieval_k}")
    print(f"retrieval_key: {args.retrieval_key}")

    main_fn(config)
    
def main():
    parser = argparse.ArgumentParser(description="Run poisoning framework experiments")

    parser.add_argument(
        "attack",
        type=str,
        help="Attack type (folder under experiments/benchmarks)"
    )

    parser.add_argument(
        "experiment",
        type=str,
        help="Experiment name (python file without .py)"
    )

    parser.add_argument(
        "--llm",
        type=str,
        default="real",
        choices=["fake","real"],
        help="Which LLM to use"
    )

    parser.add_argument(
        "--retrieval_mode",
        type=str,
        default="all",
        choices=["all","top_k","by_key","random"],
        help="Memory retrieval mode"
    )

    parser.add_argument(
        "--retrieval_k",
        type=int,
        default=None,
        help="k for top_k or random retrieval"
    )

    parser.add_argument(
        "--retrieval_key",
        type=str,
        default=None,
        help="key for by_key retrieval"
    )

    parser.add_argument(
        "--memory_path",
        type=str,
        default=None,
        help="Path to persistent memory file (default derived from experiment name)"
    )

    parser.add_argument(
        "--output_path",
        type=str,
        default=None,
        help="Path to results output file (default: derived from experiment name)"
    )

    args = parser.parse_args()
    run_experiment(args)

if __name__ == "__main__":
    main()

    
