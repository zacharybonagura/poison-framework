from typing import Optional, Dict, Any

class ExperimentConfig:
    def __init__(self, retrieval_mode: str = "all", retrieval_k: Optional[int] = None, 
                 retrieval_key: Optional[str] = None, mode: str = "fake", 
                 memory_path: Optional[str] = None, output_path: Optional[str] = None):
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.mode = mode
        self.memory_path = memory_path
        self.output_path = output_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval_mode": self.retrieval_mode,
            "retrieval_k": self.retrieval_k,
            "retrieval_key": self.retrieval_key,
            "mode": self.mode,
            "memory_path": self.memory_path,
            "output_path": self.output_path,
        }
    
