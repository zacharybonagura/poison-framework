from typing import Any, Dict, List, Optional, Callable

# AgentContext represents all information available to agent at execution time
class AgentContext:
    def __init__(
        self,
        label: str,
        system_prompt: str,
        user_input: str,
        tools: Optional[List[Any]] = None,
        memory: Optional[Any] = None,
        plan: Optional[List[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        task_checker: Optional[Callable[[str], bool]] = None,
        task_judge_spec: Optional[Dict[str, Any]] = None,
    ):
        self.label = label
        self.system_prompt = system_prompt
        self.user_input = user_input
        self.tools = tools if tools is not None else []
        self.memory = memory if memory is not None else []
        self.plan = plan if plan is not None else []
        self.metadata = metadata if metadata is not None else {}
        self.task_checker = task_checker
        self.task_judge_spec = task_judge_spec

    # Convert context to a dictionary for Attack.inject() compatibility
    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "system_prompt": self.system_prompt,
            "user_input": self.user_input,
            "tools": self.tools,
            "memory": self.memory,
            "plan": self.plan,
            "metadata": self.metadata,
            "task_checker": self.task_checker,
            "task_judge_spec": self.task_judge_spec,
        }

    # Reconstruct AgentContext from a dictionary
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        return cls(
            label=data.get("label"),
            system_prompt=data.get("system_prompt", ""),
            user_input=data.get("user_input", ""),
            tools=data.get("tools"),
            memory=data.get("memory"),
            plan=data.get("plan"),
            metadata=data.get("metadata"),
            task_checker=data.get("task_checker"),
            task_judge_spec=data.get("task_judge_spec"),
        )
