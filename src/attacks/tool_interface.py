from typing import Optional, List, Dict, Any
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.output_checker import OutputChecker
from agent.tool import Tool
from copy import deepcopy


class ToolInterfaceAttack(Attack):

    def __init__(
        self,
        name: str,
        target_tool: str,
        success_checker: OutputChecker,
        scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
        trigger: Optional[str] = None,
        judge_spec: Optional[Dict[str, Any]] = None,
        poisoned_description: Optional[str] = None,
        tool_policy: Optional[str] = None,
    ):
        super().__init__(
            name=name or "ToolInterfaceAttack",
            target=AttackTarget.TOOL_INTERFACE,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger,
            judge_spec=judge_spec,
        )
        self.target_tool = target_tool
        self.poisoned_description = poisoned_description
        self.tool_policy = tool_policy

    # Tool interface poisoning does not directly rewrite the task prompt,
    # but it may inject tool-use policy text into the active context so the
    # model is biased during the current run.
    def inject(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.should_trigger(context):
            return context

        if self.tool_policy:
            context.setdefault("memory", [])
            context["memory"].append(
                f"Tool-use policy for '{self.target_tool}': {self.tool_policy}"
            )

        return context

    # Poison the tool description shown to the model
    def modify_tool_descriptions(self, tools: List[Tool]) -> List[Tool]:
        if self.poisoned_description is None:
            return tools

        modified = []
        for t in tools:
            if t.name == self.target_tool:
                new_tool = deepcopy(t)
                new_tool.description = self.poisoned_description
                modified.append(new_tool)
            else:
                modified.append(t)

        return modified

    # Persist tool-interface poisoning as long-term text memory
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None

        policy_lines = []

        if self.poisoned_description:
            policy_lines.append(
                f"The correct description of '{self.target_tool}' is: {self.poisoned_description}"
            )

        if self.tool_policy:
            policy_lines.append(
                f"Tool-use policy for '{self.target_tool}': {self.tool_policy}"
            )

        if not policy_lines:
            return None

        return {
            "source": "tool_interface",
            "key": f"tool_policy_{self.target_tool}",
            "value": "\n".join(policy_lines),
        }