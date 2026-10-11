import os
from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class IntentResult(BaseModel):
    intent: Literal["QUERY_SALES", "QUERY_REPORT", "OTHER"] = Field("用户的业务意图.")
    month: str | None = Field(None, description="用户查询的月份，格式为YYYY-MM; 没有则为null."
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="模型对意图的置信度，范围为0到1.",
    )
    reason: str = Field(
        description="简短判断理由.",
    )

model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),)

structured_model =  model.with_structured_output(
    IntentResult,
    method="json_schema",
)

result = structured_model.invoke("查询销售额，但我还没有确定月份")

print("对象类型：", type(result).__name__)
print("意图：", result.intent)
print("月份：", result.month)
print("置信度：", result.confidence)
print("完整JSON：")
print(result.model_dump_json(indent=2))