from typing import Callable

class Tool:
    def __init__(self,name: str, description: str, func: Callable[[str], str]):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, arguments: str) -> str:
        return self.func(arguments)