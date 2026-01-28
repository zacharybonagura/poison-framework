from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
        model="meta-llama/Llama-3.2-1B-Instruct",
    base_url="http://localhost:7035/v1",
    api_key="not-needed",
    temperature=0.0,
)

print(llm.invoke("Say 'banana' and nothing else.").content)

