import os

from langchain_openai import ChatOpenAI


model = ChatOpenAI(
    model = os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

messages = [
    (
        "system", "You are an interviewer. Answer in English.",
    ),
    (
         "human", "请用两句话解释LangChain和LangGraph最根本的区别。"
    )
]

response = model.invoke(messages)

print("对象类型:", type(response).__name__)
print("响应内容:", response.text)
print("Token信息", response.usage_metadata)