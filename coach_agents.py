#定义AI Agent及其工具与运行封装

from agents import Agent, Runner, function_tool

from config import MODEL, PAST_REPORTS_DIR, PAST_SCORES_DIR
from storage import read_dir_files

#读取历史成绩数据
@function_tool
def get_past_scores() -> str:
    return read_dir_files(PAST_SCORES_DIR, ".json")

#读取历史分析报告
@function_tool
def get_past_reports() -> str:
    return read_dir_files(PAST_REPORTS_DIR, ".md")


# Agent 1：比赛规划
planning_agent = Agent(
    name="Match Planning Coach",
    model=MODEL,
    instructions="""
你是一名射击赛事规划顾问。
我现在是一位C级的USPSA射手，想要升级到B级。
你会收到从俱乐部网站抓取到的「即将进行的比赛」信息。
请专注于「参赛日程规划」。训练计划与能力提升的详细分析由成绩分析环节负责，你不必展开。

要求：
1. 按时间顺序梳理即将进行的比赛，标注日期、项目与级别
2. 给出参赛建议
3. 提示报名状态（如尚未开放报名）等需要注意的事项，并给出报名链接
4. 不要编造比赛信息中没有的内容

必须以 markdown 格式输出。
请尽量简短：多用要点/列表，避免冗长铺垫，全文控制在约 400 字以内。
""",
)

# Agent 2：成绩分析师
score_agent = Agent(
    name="Score Analyst Coach",
    model=MODEL,
    tools=[get_past_scores, get_past_reports],
    instructions="""
你是一名资深的射击运动教练与成绩分析师。
我现在是一位C级的USPSA射手，想要升级到B级。
你会收到我的比赛成绩数据（JSON 格式，每个对象是一条成绩，字段名已说明含义）。
注意这些成绩是比赛的combined成绩，而不是stage的成绩。
你可以使用以下工具：
- get_past_scores：读取历史成绩，用于对比本次与过往表现、判断趋势
- get_past_reports：读取历史分析报告，用于参考过往结论、保持建议连贯

请根据这些成绩，为我做出深入分析：
1. 总体表现评价（结合完成度、命中分布、用时）
2. 找出主要失分点（如脱靶 / 误击禁靶 / 程序罚分 / D 区偏多、命中率、速度问题等）
3. 针对升级到 B 级，指出需要重点提升的方面
4. 给出具体、可执行的训练建议，并制定一份阶段性训练计划（分周或分阶段）
5. 针对即将到来的比赛给出针对性的备赛重点
6. 不要编造成绩数据中没有的信息

必须以 markdown 格式输出。
请尽量简短：多用要点/列表，直击重点，避免冗长铺垫，全文控制在约 600 字以内。
""",
)

#运行指定 Agent 并返回文本结果，同时打印工具调用的调试信息。
def run_agent(agent: Agent, data: str) -> str:
    print("正在调用大模型，请稍候……")
    result = Runner.run_sync(agent, data)

    # 调试输出：统计本次调用了哪些工具、共几次
    tool_calls = [
        item for item in result.new_items
        if item.__class__.__name__ == "ToolCallItem"
    ]
    if tool_calls:
        names = [
            getattr(getattr(item, "raw_item", None), "name", "unknown")
            for item in tool_calls
        ]
        print(f"[调试] 本次调用工具 {len(tool_calls)} 次：{', '.join(names)}")
    else:
        print("[调试] 本次未调用任何工具")

    return result.final_output
