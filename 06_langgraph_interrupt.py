from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class SettlementState(TypedDict):
    """State of the settlement process."""
    total_sales: float
    refunds: float
    creator_rate: float
    creator_amount: float
    valid_sales: float | None
    approved: bool | None
    report: str

def calculate(state: SettlementState) -> dict:
    valid_sales = state["total_sales"] - state["refunds"]
    amount = round(valid_sales * state["creator_rate"], 2)

    print(f"[calculate] 计算得到: {amount}")

    return {"creator_amount": amount, "valid_sales": valid_sales}

def generate_report(state: SettlementState) -> dict:
    print(f"[generate_report] 生成结算报告...")

    return {
        "report": f"创作者应收金额: {state['creator_amount']}元。 "
    }

def route_after_calculate(state: SettlementState) -> str:
    if state["creator_amount"] > 10000:
        return "review"

    return "report"

def human_review(state: SettlementState) -> dict:
    print("[human_review] 进入审批节点")

    decision = interrupt({
        "question": "是否批准这次结算？",
        "creator_amount": state["creator_amount"],
        "valid_sales": state["valid_sales"]
    })

    print(f"[human_review] 收到审批结果: {decision}")

    return {"approved": decision}

def route_after_review(state: SettlementState) -> str:
    if state["approved"] is True:
        return "approved"

    return "rejected"

def reject_request(state: SettlementState) -> dict:
    print("[reject_request] 结算请求被拒绝。")

    return {"report": "结算请求被拒绝。"}



builder = StateGraph(SettlementState)

builder.add_node("calculate", calculate)
builder.add_node("human_review", human_review)
builder.add_node("generate_report", generate_report)
builder.add_node("reject_request", reject_request)

builder.add_edge(START, "calculate")
builder.add_conditional_edges("calculate", route_after_calculate, {
    "review": "human_review",
    "report": "generate_report",
})
builder.add_conditional_edges("human_review", route_after_review, {
    "approved": "generate_report",
    "rejected": "reject_request",
})
builder.add_edge("generate_report", END)
builder.add_edge("reject_request", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)



if __name__ == "__main__":
    initial_state: SettlementState = {
        "total_sales": 100000.0,
        "refunds": 5000.0,
        "creator_rate": 0.85,
        "creator_amount": 0.0,
        "valid_sales": 0.0,
        "approved": None,
        "report": "",
    }

    config = {
        "configurable": {
            "thread_id": "settlement-demo-001"
        }
    }

    # 第一次运行：可能在审批节点暂停
    result = graph.invoke(initial_state, config=config)

    if result.get("__interrupt__"):
        print("/n[工作流已暂停]")
        print("审批内容：", result["__interrupt__"][0].value)

        #  此时invoke已返回，外部程序可以处理其他事情
        snapshot = graph.get_state(config)
        print("已保存的状态：", snapshot.values)
        print("待执行节点:", snapshot.next)

        answer = input("\n是否批准?请输入y或者n: ").strip().lower()

        while answer not in {"y", "n"}:
            answer = input("请输入y或者n").strip().lower()

        # 使用相同thread_id,恢复原来任务
        result = graph.invoke(
            Command(resume=(answer == "y")),
            config=config
        )


    print("\n[最终结果] ", result)
    print("\n[报告内容] ", result["report"])