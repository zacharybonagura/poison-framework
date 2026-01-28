from typing import Any, Dict, List, Optional

# AgentContext represents all information available to agent at execution time
class AgentContext:
    def __init__(
        self,
        system_prompt: str,
        user_input: str,
        tools: Optional[List[Any]] = None,
        memory: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.system_prompt = system_prompt
        self.user_input = user_input
        self.tools = tools if tools is not None else []
        self.memory = memory if memory is not None else []
        self.metadata = metadata if metadata is not None else {}

    # Convert context to a dictionary for Attack.inject() compatibility
    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "user_input": self.user_input,
            "tools": self.tools,
            "memory": self.memory,
            "metadata": self.metadata,
        }

    # Reconstruct AgentContext from a dictionary
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        return cls(
            system_prompt=data.get("system_prompt", ""),
            user_input=data.get("user_input", ""),
            tools=data.get("tools"),
            memory=data.get("memory"),
            metadata=data.get("metadata"),
        )
