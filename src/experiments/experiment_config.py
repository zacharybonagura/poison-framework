from typing import Optional, Dict, Any

# ExperimentConfig encapsulates all configuration parameters for a single experiment run
class ExperimentConfig:
    def __init__(self, retrieval_mode: str = "all", retrieval_k: Optional[int] = None, 
                 retrieval_key: Optional[str] = None, mode: str = "fake", num_trials: int = 1,
                 memory_path: Optional[str] = None, results_path: Optional[str] = None,
                 judge_mode: str = "off", # off, fake, real
                 judge_model: str = "meta-llama/Llama-3.2-1B-Instruct",
                 task_judge_strategy: str = "rule", # rule, judge, hybrid
                 attack_judge_strategy: str = "rule", # rule, judge, hybrid
                ):
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.mode = mode
        self.num_trials = num_trials
        self.memory_path = memory_path
        self.results_path = results_path
        self.judge_mode = judge_mode
        self.judge_model = judge_model
        self.task_judge_strategy = task_judge_strategy
        self.attack_judge_strategy = attack_judge_strategy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval_mode": self.retrieval_mode,
            "retrieval_k": self.retrieval_k,
            "retrieval_key": self.retrieval_key,
            "mode": self.mode,
            "num_trials": self.num_trials,
            "memory_path": self.memory_path,
            "results_path": self.results_path,
            "judge_mode": self.judge_mode,
            "judge_model": self.judge_model,
            "task_judge_strategy": self.task_judge_strategy,
            "attack_judge_strategy": self.attack_judge_strategy,
        }
    
