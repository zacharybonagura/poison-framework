from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms.fake import FakeListLLM
from typing import Optional, Tuple, Dict, Any, List

from attacks.Attack import Attack, PoisoningScope
from agent.AgentContext import AgentContext
from agent.MemoryStore import MemoryStore

# AgentRunner is where the agent retrieves, injects, executes, and persists
class AgentRunner:
    def __init__(self, retrieval_mode="all", retrieval_k=None, 
                 retrieval_key=None, memory_path: str="persisted_memory.json"):
        self.llm = self._build_llm()
        self.prompt = self._build_prompt()
        self.executor = self._build_executor()
        
        self.retrieval_mode = retrieval_mode
        self.retrieval_k = retrieval_k
        self.retrieval_key = retrieval_key
        self.persistent_memory = MemoryStore(path=memory_path)
        self.session_memory: List[str] = []

    # Build a fake LLM for testing (replace later with real LLM)
    def _build_llm(self):
        return FakeListLLM(responses=[
            "[FAKE] response 1",
            "[FAKE] response 2",
            "[FAKE] response 3",
        ])

    # Define the base prompt template used by the agent
    def _build_prompt(self):
        return ChatPromptTemplate.from_template(
            """
            {system_prompt}
            Relevant memory:
            {memory}
            User query:
            {user_input}
            """
        )

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

    def run(self, context: AgentContext, attack: Optional[Attack] = None) -> Tuple[str, Dict[str, Any]]:
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

        # Apply attack injection if trigger condition is met
        did_trigger = False
        if attack is not None and attack.should_trigger(context):
            did_trigger = True
            context = attack.inject(context)

        output = str(self.executor.invoke(context))

        # Evaluate whether the attack succeeded
        success = False
        if attack is not None and did_trigger:
            success = attack.detect_success(output)
        
        # Persist memory if scope is set
        longterm_persisted = None
        if attack is not None and did_trigger:
            longterm_persisted = attack.persist_longterm()

            if attack.scope == PoisoningScope.PERSISTENT and longterm_persisted is not None and "key" in longterm_persisted and "value" in longterm_persisted:
                self.persistent_memory.add_unique(longterm_persisted["key"], longterm_persisted["value"])
            elif attack.scope == PoisoningScope.SESSION:
                val = attack.persist_session()
                if val: self.session_memory.append(val)
        
        info = {
            "attack": attack.metadata() if attack is not None else None,
            "did_trigger": did_trigger,
            "success": success,
            "longterm_persisted": longterm_persisted,
            "persistent_memory_size": len(self.persistent_memory.load()),
            "session_memory_size": len(self.session_memory)
        }

        return output, info
     
