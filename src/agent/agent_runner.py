import json
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
            ("system", "Relevant information from memory to use in your response:\n{memory}"),
            ("system", "Available tools:\n{tool_descriptions}"),
            ("system", "Tool observations:\n{tool_observations}"),
            ("user", "{user_input}")
        ])

    # Create the runnable chain: format inputs, apply prompt, call LLM
    def _build_executor(self):
        return (
            {
                "system_prompt": RunnableLambda(lambda x: x["system_prompt"]),
                "memory": RunnableLambda(lambda x: "\n".join(x["memory"]) if x.get("memory") else "None"),
                "tool_descriptions": RunnableLambda(lambda x: "\n".join(f"{t.name}: {t.description}" 
                                                                        for t in x.get("tools", [])) if x.get("tools") else "None"),
                "tool_observations": RunnableLambda(lambda x: "\n".join(x["tool_observations"]) if x.get("tool_observations") else "None"),
                "user_input": RunnableLambda(lambda x: x["user_input"]),
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

    def run(self, context: AgentContext, attack: Optional[Attack] = None) -> str:
        context = context.to_dict()
        
        # Load persistent memory (values) based on retrieval mode and append to current memory
        persistent_values = self.persistent_memory.retrieve(
            mode=self.retrieval_mode,
            k=self.retrieval_k,
            key=self.retrieval_key
        )

        if persistent_values:
            context["memory"] = context["memory"] + persistent_values

        tools = context["tools"]

        if attack: 
            tools = attack.modify_tool_descriptions(tools)
            context["tools"] = tools

        result = self.executor.invoke(context)

        # Extract just the model text output
        if hasattr(result, "content"):
            output = result.content
        else:
            output = str(result)

        # Check if output is a tool call
        try:
            parsed = json.loads(output)
        except:
            return output # Not a tool call, return directly

        if "action" in parsed and "input" in parsed:
            tool_name = parsed["action"]
            tool_input = parsed["input"]

            if attack: tool_name, tool_input = attack.modify_tool_call(tool_name, tool_input)

            tool = next((t for t in context["tools"] if t.name == tool_name), None)
            if tool is None: return f"Error: Tool '{tool_name}' not found."

            tool_result = tool.execute(tool_input)

            if attack: tool_result = attack.modify_tool_output(tool_name, tool_result)

            context["tool_observations"].append(f"Tool '{tool_name}' returned: {tool_result}")
            result = self.executor.invoke(context)

            if hasattr(result, "content"):
                output = result.content
            else:
                output = str(result)

        return output
     
