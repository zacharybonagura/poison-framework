from typing import Dict, Any, Callable
import json

class Tool:
    def __init__(self,name: str, description: str, schema: Dict[str, Any], func: Callable[[str], str]):
        self.name = name
        self.description = description
        self.schema = schema
        self.func = func
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        return self.func(arguments)

    def format_for_prompt(self) -> str:
        return f"{self.name}: {self.description}\nSchema: {json.dumps(self.schema, indent=2)}"