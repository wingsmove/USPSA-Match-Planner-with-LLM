#定义AI Agent及其工具与运行封装

import json
import os
import sqlite3

from agents import Agent, ModelSettings, Runner, function_tool

from config import MAX_PAST_REPORTS, MODEL, PAST_REPORTS_DIR
from storage import read_dir_files

# backend/app.db 的绝对路径（本文件在 backend/LLMs/ 下，app.db 在 backend/ 下）
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.db")

#读取历史成绩数据（从数据库 scores 表读取）
@function_tool
def get_past_scores() -> str:
    if not os.path.exists(_DB_PATH):
        return "（数据库不存在或暂无成绩）"
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row  # 让每行可按列名取值
    try:
        rows = conn.execute("SELECT * FROM scores ORDER BY id").fetchall()
    except sqlite3.OperationalError:
        return "（数据库中没有 scores 表）"
    finally:
        conn.close()
    if not rows:
        return "（数据库暂无成绩）"
    records = [dict(row) for row in rows]
    return json.dumps(records, ensure_ascii=False, indent=2, default=str)

#读取最近的历史分析报告（限制数量，避免上下文过长）
@function_tool
def get_past_reports() -> str:
    return read_dir_files(PAST_REPORTS_DIR, ".md", limit=MAX_PAST_REPORTS)

#读取最新一场成绩的 class，作为射手当前的 class；没有过往成绩则默认 U（未定级）
@function_tool
def get_class() -> str:
    if not os.path.exists(_DB_PATH):
        return "U"
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT shooter_class FROM scores ORDER BY id DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        return "U"
    finally:
        conn.close()
    if not row or not row["shooter_class"]:
        return "U"
    return row["shooter_class"]


# Agent 1：比赛规划
planning_agent = Agent(
    name="Match Planning Coach",
    model=MODEL,
    tools=[get_past_scores, get_class],
    model_settings=ModelSettings(tool_choice="get_class"),  # 强制先调用 get_class
    instructions="""
你是一名射击赛事规划顾问。
你会收到从俱乐部网站抓取到的「即将进行的比赛」信息。
请专注于「参赛日程规划」。训练计划与能力提升的详细分析由成绩分析环节负责，你不必展开。
你必须使用以下工具：
- get_class：读取我当前的 USPSA 级别（U/D/C/B/A/M/GM）
- get_past_scores：读取历史成绩，用于参考过往比赛安排、保持建议连贯

在给出规划前，必须首先调用 get_class 确定我当前的级别，并据此推荐合适级别的比赛
（例如当前 C 级则以升 B 级为目标，当前 B 级则以升 A 级为目标；U 级则以入门为目标; GM则以拿到大赛冠军为目标）。

要求：
1. 按时间顺序梳理即将进行的比赛，标注日期、项目与级别
2. 给出参赛建议
3. 提示报名状态（如尚未开放报名）等需要注意的事项，给出报名链接
4. 给出简短的训练建议
5. 不要编造比赛信息中没有的内容

必须以 markdown 格式输出。
请尽量简短：多用要点/列表，避免冗长铺垫，全文（不包括比赛名称，等级，俱乐部和比赛报名链接等）控制在约 400 字以内。
""",
)

# Agent 2：成绩分析师
score_agent = Agent(
    name="Score Analyst Coach",
    model=MODEL,
    tools=[get_past_scores, get_past_reports, get_class],
    model_settings=ModelSettings(tool_choice="get_class"),  # 强制先调用 get_class
    instructions="""
你是一名资深的射击运动教练与成绩分析师。
你会收到我的比赛成绩数据（JSON 格式，每个对象是一条成绩，字段名已说明含义）。
注意这些成绩是比赛的combined成绩，而不是stage的成绩。
你必须使用以下工具：
- get_class：读取最新一场成绩的 class，作为我当前的 USPSA 级别（U/D/C/B/A/M/GM）
- get_past_scores：读取历史成绩，用于对比本次与过往表现、判断趋势
如果你发现成绩出现异常，需要进一步分析，请使用以下工具：
- get_past_reports：读取历史分析报告，用于参考过往结论、保持建议连贯

分析前必须首先调用 get_class 确定我当前的级别，并据此给出「升到下一个级别」的针对性建议
（例如当前 C 级则以升 B 级为目标，当前 B 级则以升 A 级为目标；U 级则以入门为目标; GM则以拿到大赛冠军为目标）。

请根据这些成绩，为我做出深入分析：
1. 总体表现评价（结合完成度、命中分布、用时）
2. 找出主要失分点（如脱靶 / 误击禁靶 / 程序罚分 / D 区偏多、命中率、速度问题等）
3. 针对从当前级别升到下一个级别，指出需要重点提升的方面
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
