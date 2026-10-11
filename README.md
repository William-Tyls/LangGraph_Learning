# LangChain & LangGraph Learning

从模型调用、结构化输出和工具调用，到 Agent、条件工作流与人工审批的 Python 学习记录。
示例以模拟销售查询和结算为背景，重点观察消息流、状态更新与执行路径。

## 学习顺序

| 文件 | 学习内容 |
| --- | --- |
| `01_model_call.py` | 消息角色、模型调用、响应内容与 Token 信息 |
| `02_structured_output.py` | Pydantic Schema、意图识别、结构化 JSON 输出 |
| `03_tool_calling.py` | 手动执行工具调用，将 ToolMessage 返回模型 |
| `04_langchain_agent.py` | create_agent、多工具协作、ToolStrategy 结构化结果 |
| `05_langgraph_workflow copy.py` | State、节点、条件边、审批通过与拒绝分支 |
| `06_langgraph_interrupt.py` | interrupt、Checkpoint、thread_id 与 Command 恢复 |

## 安装

以下命令适用于 macOS / Linux；本地验证环境为 Python 3.12.7。

```bash
git clone https://github.com/William-Tyls/LangGraph_Learning.git
cd LangGraph_Learning
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` 固定了当前环境的主要依赖版本，不是完整的传递依赖锁文件。

## 运行

前四个示例需要可用的模型 API 密钥。通过环境变量配置，勿将真实密钥写入代码或提交到 Git。

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-5-nano"

python 01_model_call.py
python 02_structured_output.py
python 03_tool_calling.py
python 04_langchain_agent.py
```

默认模型为 `gpt-5-nano`，可通过 `OPENAI_MODEL` 替换为账户支持的模型；
结构化输出和工具调用示例需要模型支持相应能力。脚本目前读取 shell 环境变量，不会自动加载 `.env`。
运行这些示例会产生 API 请求及相应费用。

第 4 个示例默认执行结构化结算请求；文件内的 `run_case()` 可用于查看逐条消息，
练习普通问答、缺失月份和无数据月份。模拟数据库仅提供 `2026-08`。

后两个示例只使用本地模拟数据，不需要 API 密钥：

```bash
python "05_langgraph_workflow copy.py"
python 06_langgraph_interrupt.py
```

第 5 个示例将 `approved` 预设为 `False`，默认进入拒绝分支。
第 6 个示例在审批节点暂停，在终端输入 `y` 或 `n` 后，使用相同 `thread_id` 恢复任务。

## 工作流

```text
START → calculate
           ├─ 创作者应收金额 ≤ 10,000 → generate_report → END
           └─ 创作者应收金额 > 10,000 → human_review
                                          ├─ 通过 → generate_report → END
                                          └─ 拒绝 → reject_request → END
```

`06_langgraph_interrupt.py` 使用 `InMemorySaver`：状态只保存在当前进程内，
退出或重启程序后不会保留。`thread_id` 是工作流任务标识，不代表操作系统线程。
恢复时审批节点会重新开始执行，因此 `interrupt()` 之前的代码也可能再次执行。

## 练习边界

- 所有销售数据均为模拟数据，没有连接真实 POS，不会真实付款或发送报告。
- 不同练习的模拟金额、币种和审批阈值独立设置，并非统一业务规则。
- 金额当前用浮点数演示；真实结算应使用整数最小货币单位或 Decimal，并补充校验。
- 结构化输出中的 `confidence` 是模型生成的自评分，不是经过校准的概率。
- 后续练习方向：持久化 Checkpointer、失败处理、幂等性和工作流测试。

## 学习资料

- [LangChain 文档](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph 文档](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangChain Academy](https://academy.langchain.com/)

## License

见 [LICENSE](LICENSE)。
