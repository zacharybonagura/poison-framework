from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
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
        self.session_memory: List[str] = []

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
            ("system", "You must follow these user preferences in all responses:\n{memory}"),
            ("user", "{user_input}")
        ])

    # Create the runnable chain: format inputs, apply prompt, call LLM
    def _build_executor(self):
        return (
            {
                "system_prompt": RunnableLambda(lambda x: x["system_prompt"]),
                "memory": RunnableLambda(lambda x: "\n".join(x["memory"]) if x.get("memory") else "None"),
                "user_input": RunnableLambda(lambda x: x["user_input"]),
            }
            | self.prompt
            | self.llm
        )

    def reset_session(self) -> None:
        self.session_memory = []

    # Inject an attack into the agent
    def inject_attack(self, context: AgentContext, attack: Attack) -> Dict[str, Any]:
        context_dict = context.to_dict()

        # Apply attack injection if trigger condition is met
        did_trigger = False
        if attack.should_trigger(context_dict):
            did_trigger = True
            context_dict = attack.inject(context_dict)

            # Persist memory if scope is set
            if attack.scope == PoisoningScope.PERSISTENT:
                persisted = attack.persist_longterm()
                if persisted:
                    self.persistent_memory.add_entry(
                        persisted["key"],
                        persisted["value"],
                        persisted.get("source", "benign")
                    )
            elif attack.scope == PoisoningScope.SESSION:
                val = attack.persist_session()
                if val: self.session_memory.append(val)

        return {
            "did_trigger": did_trigger,
            "attack": attack.metadata(),
        }

    def run(self, context: AgentContext) -> Tuple[str, Dict[str, Any]]:
        context = context.to_dict()

        # Load persistent memory (values) based on retrieval mode and append to current memory
        persistent_values = self.persistent_memory.retrieve(
            mode=self.retrieval_mode,
            k=self.retrieval_k,
            key=self.retrieval_key
        )

        if persistent_values:
            context["memory"] = context["memory"] + persistent_values

        if self.session_memory:
            context["memory"] = context["memory"] + self.session_memory

        output = str(self.executor.invoke(context))

        return output
     
