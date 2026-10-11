import os

from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

@tool
def get_monthly_sales(month: str) -> str:
    """查询指定月份的销售额，返回格式为：YYYY-MM: 销售额"""
    # 这里可以调用实际的数据库或API来获取销售数据

    print(f"\n[python正在执行工具] 查询月份: {month}")

    # 暂时使用模拟数据
    return {
        "month": month,
        "total_sales": 1000000.0,
        "refunds": 50000.0,
        "valid_sales": 950000.0,
        "currency": "CNY",
    }

model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),)

model_with_tools = model.bind_tools([get_monthly_sales], strict=True)

messages = [
    HumanMessage(
        content="请帮我查询2023年5月的销售额，并用中文回答。"
    )
]

# 第一次调用，模型只决定用什么工具，传什么参数
ai_message = model_with_tools.invoke(messages)

print("模型首次返回的文本:", ai_message.text)
print("模型生成的工具调用:", ai_message.tool_calls)

messages.append(ai_message)

tools_by_name = {
    get_monthly_sales.name: get_monthly_sales,
}

# Python程序真正执行工具，获取结果
for tool_call in ai_message.tool_calls:
    selected_tool = tools_by_name[tool_call["name"]]

    tool_result = selected_tool.invoke(tool_call["args"])

    print("工具执行结果:", tool_result)

    messages.append(
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
        )
    )


# 第二次调用，模型根据工具执行结果生成最终回答
final_response = model_with_tools.invoke(messages)

print("模型最终回答:", final_response.text)