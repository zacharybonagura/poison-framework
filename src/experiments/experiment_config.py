from typing import Optional, Dict, Any

# ExperimentConfig encapsulates all configuration parameters for a single experiment run
class ExperimentConfig:
    def __init__(self, retrieval_mode: str = "all", retrieval_k: Optional[int] = None, 
                 retrieval_key: Optional[str] = None, mode: str = "fake", num_trials: int = 1,
                 memory_path: Optional[str] = None, output_path: Optional[str] = None):
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.mode = mode
        self.num_trials = num_trials
        self.memory_path = memory_path
        self.output_path = output_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval_mode": self.retrieval_mode,
            "retrieval_k": self.retrieval_k,
            "retrieval_key": self.retrieval_key,
            "mode": self.mode,
            "num_trials": self.num_trials,
            "memory_path": self.memory_path,
            "output_path": self.output_path,
        }
    
