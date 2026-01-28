from typing import Optional, Dict, Any

class ExperimentConfig:
    def __init__(self, rounds: int = 1,  retrieval_mode: str = "all",
                 retrieval_k: Optional[int] = None, retrieval_key: Optional[str] = None, 
                 memory_path: str = "experiments/memory/exp_memory.json", 
                 output_path: str = "experiments/results/exp_results.jsonl"):
        self.rounds = rounds
        self.memory_path = memory_path
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.output_path = output_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rounds": self.rounds,
            "retrieval_mode": self.retrieval_mode,
            "retrieval_k": self.retrieval_k,
            "retrieval_key": self.retrieval_key,
            "memory_path": self.memory_path,
            "output_path": self.output_path,
        }
    
