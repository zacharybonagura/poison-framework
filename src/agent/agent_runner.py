import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_community.llms.fake import FakeListLLM
from typing import Optional, Tuple, Dict, Any, List

from attacks.attack import Attack, PoisoningScope
from agent.agent_context import AgentContext
from agent.memory_store import MemoryStore

# AgentRunner is where the agent retrieves, injects, executes, and persists
class AgentRunner:
    def __init__(self, retrieval_mode="all", retrieval_k=None, 
                 retrieval_key=None, memory_path: str="persisted_memory.json",
                 llm_mode: str = "fake"):
        self.llm_mode = llm_mode
        self.llm = self._build_llm()
        self.prompt = self._build_prompt()
        self.executor = self._build_executor()
        
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.persistent_memory = MemoryStore(path=memory_path)

    # Build an LLM
    def _build_llm(self):
        if self.llm_mode == "fake":
            return self._build_llm_fake()

        elif self.llm_mode == "real":
            return ChatOpenAI(
                model="meta-llama/Llama-3.2-1B-Instruct",
                base_url="http://localhost:7035/v1",
                api_key="not-needed",
                temperature=0.0,
            )

        else:
            raise ValueError(f"Unknown llm_mode: {self.llm_mode}")

    # Build a fake LLM for testing
    def _build_llm_fake(self):
        return FakeListLLM(responses=[
            "[FAKE] response 1",
            "[FAKE] response 2",
            "[FAKE] response 3",
        ])
    
    # Define the base prompt template used by the agent
    def _build_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("system", "Relevant memory to use in your response:\n{memory}"),
            ("system", "{tool_block}"),
            ("user", "{user_input}"),
            ("system", "{scratchpad}")
        ])

    # Create the runnable chain: format inputs, apply prompt, call LLM
    def _build_executor(self):
        return (
            {
                "system_prompt": RunnableLambda(lambda x: x["system_prompt"]),
                "memory": RunnableLambda(lambda x: "\n".join(x["memory"]) if x.get("memory") else "None"),
                "tool_block": RunnableLambda(lambda x: (
f"""Available tools:
{"\n".join(t.format_for_prompt() for t in x.get("tools", []))}

If you need to use a tool, respond ONLY with valid JSON in this format:

{{
    "tool_call": {{
        "name": "<tool_name>",
        "arguments": {{ ... }}
    }}
}}

After receiving tool results:
- Do NOT call the tool again unless absolutely necessary.
- You may call a tool at most once unless the user explicitly requests new information.
- Use the tool result to produce a final natural language answer.

If no tool is needed, respond with a normal final answer.
""" if x.get("tools") else "")),
                "user_input": RunnableLambda(lambda x: x["user_input"]),
                "scratchpad": RunnableLambda(lambda x: x.get("scratchpad", ""))
            }
            | self.prompt
            | self.llm
        )

    # Inject an attack into the agent's prompt
    def inject_attack_into_prompt(self, context: AgentContext, attack: Attack) -> Tuple[bool, AgentContext]:
        context_dict = context.to_dict()

        # Apply attack injection if trigger condition is met
        did_trigger = False
        if attack.should_trigger(context_dict):
            did_trigger = True
            context_dict = attack.inject(context_dict)

        return did_trigger, AgentContext.from_dict(context_dict)

    # Inject an attack into the agent's memory
    def inject_attack_into_memory(self, context: AgentContext, attack: Attack) -> Dict[str, Any]:
        context_dict = context.to_dict()

        # Apply attack injection if trigger condition is met
        did_trigger = False
        if attack.should_trigger(context_dict):
            did_trigger = True

            # Persist memory if scope is set
            if attack.scope == PoisoningScope.PERSISTENT:
                persisted = attack.persist_longterm()
                if persisted:
                    self.persistent_memory.add_entry(
                        persisted["key"],
                        persisted["value"],
                        persisted.get("source", "benign")
                    )

        return {
            "did_trigger": did_trigger,
            "attack": attack.metadata(),
        }

    # Get the tool from json output from model
    def _extract_tool_call(self, output: str):
        try:
            data = json.loads(output)
            return data.get("tool_call")
        except:
            return None
        
    def run(self, context: AgentContext, attack: Optional[Attack] = None) -> str:
        context = context.to_dict()
        context.setdefault("scratchpad", "")

        # Load persistent memory (values) based on retrieval mode and append to current memory
        persistent_values = self.persistent_memory.retrieve(
            mode=self.retrieval_mode,
            k=self.retrieval_k,
            key=self.retrieval_key
        )

        # Add persistent memory information into model's memory
        if persistent_values:
            context["memory"] = context["memory"] + persistent_values

        # Update descriptions of tools if attack before asking model any query
        if attack and attack.scope == PoisoningScope.SINGLE_INSTANCE: 
            tools = attack.modify_tool_descriptions(context["tools"])
            context["tools"] = tools

        max_steps = 5
        step = 0
        while step < max_steps:
            print(step)
            print(context["memory"])
            result = self.executor.invoke(context)
            output = getattr(result, "content", result)
            tool_call = self._extract_tool_call(output)

            if tool_call: # if tool is called, we must call the agent again using the tool's result 
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]

                if attack and attack.scope == PoisoningScope.SINGLE_INSTANCE:
                    tool_name, tool_args = attack.modify_tool_call(tool_name, tool_args)

                tool = next((t for t in context["tools"] if t.name == tool_name), None)
                if tool is None:
                    return f"Error: Tool {tool_name} not found"
                
                tool_result = tool.execute(tool_args)

                if attack and attack.scope == PoisoningScope.SINGLE_INSTANCE:
                    tool_result = attack.modify_tool_output(tool_name, tool_result)

                # context["tools"] = []

                context["scratchpad"] += f"""
The tool '{tool_name}' returned: {tool_result} 

Provide the final answer to the user in plain natural language.
Do NOT output JSON.
Do NOT call the tool '{tool_name}' again.
"""
                
                step += 1
                continue
            else:
                return output

        return "Error"
     
