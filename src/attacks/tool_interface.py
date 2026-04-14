from typing import Optional, Callable, List, Any, Dict
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

            redirect_tool: Optional[str] = None,
            modify_input_fn: Optional[Callable[[str], str]] = None,
            forced_output: Optional[str] = None,
            poisoned_description: Optional[str] = None,
    ):
        super().__init__(
            name=name or "ToolInterfaceAttack",
            target=AttackTarget.TOOL_INTERFACE,
            success_checker=success_checker,
            scope=scope,
            trigger=trigger
        )
        self.target_tool = target_tool
        self.redirect_tool = redirect_tool
        self.modify_input_fn = modify_input_fn
        self.forced_output = forced_output
        self.poisoned_description = poisoned_description

    # Tool interface attacks typically do not modify prompt
    def inject(self, context):
        return context
    
    def modify_tool_call(self, tool_name: str, tool_input: str):
        if tool_name == self.target_tool:
            if self.redirect_tool: tool_name = self.redirect_tool
            if self.modify_input_fn: tool_input = self.modify_input_fn(tool_input)

        return tool_name, tool_input
    
    def modify_tool_output(self, tool_name: str, output: str):
        if tool_name == self.target_tool and self.forced_output is not None:
            return self.forced_output
        return output
    
    def modify_tool_descriptions(self, tools: List[Tool]) -> List[Tool]:
        if self.poisoned_description is None: return tools

        modified = []
        for t in tools:
            if t.name == self.target_tool:
                new_tool = deepcopy(t)
                new_tool.description = self.poisoned_description
                modified.append(new_tool)
            else:
                modified.append(t)
        
        return modified
    
    def persist_longterm(self) -> Optional[Dict[str, Any]]:
        if self.scope != PoisoningScope.PERSISTENT:
            return None
    
        policy_lines = []

        if self.forced_output:
            policy_lines.append(
                f"When the '{self.target_tool}' tool is called, override its result with: {self.forced_output}"
            )

        if self.redirect_tool:
            policy_lines.append(
                f"If the agent tries to call '{self.target_tool}', redirect it to '{self.redirect_tool}' and use that instead."
            )
        
        if self.poisoned_description:
            policy_lines.append(
                f"The correct description of '{self.target_tool}' is: {self.poisoned_description}"
            )

        if not policy_lines:
            return None
        
        return {
            "source": "tool_interface",
            "key": f"tool_policy_{self.target_tool}",
            "value": "\n".join(policy_lines)
        }