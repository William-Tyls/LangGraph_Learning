import os

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
from pydantic import BaseModel
from langchain.agents.structured_output import ToolStrategy

model = ChatOpenAI(
    model = os.getenv("OPENAI_MODEL", "gpt-5-nano"),
)

@tool
def get_monthly_sales(month: str) -> str:
    """查询指定月份的销售数据, month格式必须为YYYY-MM."""
    print(f"\n[执行工具] get_monthly_sales(month={month!r})")

    # 模拟数据库：目前只有这一个月的数据
    database = {
        "2026-08": {
            "total_sales": 10000.0,
            "refunds": 500.0,
        }
    }

    if month not in database:
        return {"month": month, "error": "没有找到该月份的销售数据."}

    return {"month": month, **database[month]}

@tool
def calculate_settlement(
    total_sales: float,
    refunds: float,
    creator_rate: float = 0.85,
) -> dict:
    """计算结算金额。creator_rate是创作者的分成比例，取值为0到1，例如85%传0.85."""
    print(
        "\n[执行工具] calculate_settlement(" \
        f"total_sales={total_sales},"
        f"refunds={refunds},"
        f"creator_rate={creator_rate})"
    )

    if not 0 <= creator_rate <= 1:
        return {"error": "creator_rate必须在0到1之间."}

    valid_sales = total_sales - refunds
    creator_amount = round(valid_sales * creator_rate, 2)

    return {
        "valid_sales": valid_sales,
        "creator_amount": creator_amount,
        "needs_review": valid_sales > 80000,  # 如果有效销售额大于80000元，则需要人工复核
    }

SYSTEM_PROMPT = """
你是一个使用模拟销售数据的结算助手。

规则：
1. 查询销售数据必须调用 get_monthly_sales。
2. 计算结算金额必须调用 calculate_settlement。
3. 生成结算结果前，需要明确月份和创作者分成比例。
4. 缺少月份或分成比例时，向用户追问，不得自行猜测。
5. 月份传入工具前转为 YYYY-MM；百分比分成转为 0 到 1 的小数。
6. 工具返回 error 时，说明问题，不得编造数据或继续用虚构数据计算。
7. 普通介绍或问候可以直接回答。
8. 当前只能查询和计算，不会真正发送报告或付款。
"""

agent = create_agent(
    model=model,
    tools=[get_monthly_sales, calculate_settlement],
    system_prompt=SYSTEM_PROMPT,
)

def run_case(user_input: str):
    print(f"\n[用户输入] {user_input}")

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })

    for index, message in enumerate(result["messages"], start=1):
        print(f"\n--- 消息 {index}: {type(message).__name__} ---")
        print("content:", message.content)

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("tool_calls:", tool_calls)

        if message.type == "tool":
            print("tool_call_id:", message.tool_call_id)

    return result

class SettlementResult(BaseModel):
    month: str
    valid_sales: float
    creator_amount: float
    needs_review: bool

structured_agent = create_agent(
    model=model,
    tools=[get_monthly_sales, calculate_settlement],
    system_prompt=SYSTEM_PROMPT,
    response_format=ToolStrategy(SettlementResult),
)

result = structured_agent.invoke({
    "messages": [
        {"role": "user", "content": "请计算2026年8月的结算金额，创作者分成比例是85%."}
    ]
})

print(result["structured_response"].model_dump_json(indent=2))

# if __name__ == "__main__":
#     # 测试用例
#     run_case("请计算2026年9月的结算金额，创作者分成比例是85%。")
