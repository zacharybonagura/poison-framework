from typing import Optional, Callable, List
from attacks.attack import Attack, AttackTarget, PoisoningScope
from attacks.success_checker import SuccessChecker
from agent.tool import Tool
from copy import deepcopy

class ToolInterfaceAttack(Attack):

    def __init__(
            self,
            target_tool: str,
            success_checker: SuccessChecker,
            scope: PoisoningScope = PoisoningScope.SINGLE_INSTANCE,
            trigger: Optional[str] = None,

            redirect_tool: Optional[str] = None,
            modify_input_fn: Optional[Callable[[str], str]] = None,
            forced_output: Optional[str] = None,
            poisoned_description: Optional[str] = None,
    ):
        super().__init__(
            name="ToolInterfaceAttack",
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