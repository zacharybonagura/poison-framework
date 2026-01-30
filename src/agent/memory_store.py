import json
import os
from typing import List, Dict, Optional
import random

# MemoryStore represents the interface to load/store persistent entries
class MemoryStore:
    def __init__(self, path: str = "persistent_memory.json"):
        self.path = path
    
    # Load all stored memories from disk
    def load(self) -> List[Dict[str,str]]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        entries = data.get("entries", [])

        return entries
    
    # Overwrite memory store with given entries
    def save(self, entries: List[Dict[str, str]]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"entries": entries}, f, indent=2)


    # Remove any malicious entries from memory
    def reset_poison(self) -> None:
        entries = self.load()
        cleaned = [e for e in entries if e.get("source") == "benign"]
        self.save(cleaned)

    # Add a (key, value) memory entry
    # The key represents a trigger, and the value represents the text associated with it
    def add_entry(self, key: str, value: str, source: str) -> None:
        entries = self.load()
        entries.append({
            "key": key,
            "value": value,
            "source": source,
        })
        self.save(entries)

    # Return memory values based on retrieval type
    def retrieve(self, mode: str = "all", k: Optional[int] = None, key: Optional[str] = None) -> List[str]:
        entries = self.load()

        if mode == "all":
            selected = entries
        elif mode == "top_k":
            if k is None: return []
            selected = entries[-k:]
        elif mode == "by_key":
            if key is None: return []
            selected = [e for e in entries if e.get("key") == key]
        elif mode == "random":
            if k is None: return []
            selected = random.sample(entries, min(k,len(entries)))
        else:
            raise ValueError(f"Unknown retrieval mode: {mode}")
        
        return [e.get("value", "") for e in selected if e.get("value")]