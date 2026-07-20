import json
import os
from datetime import datetime

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

from scraper import format_matches_text, get_upcoming_matches_text, scrape_all

load_dotenv()

MATCHES_DIR = "Matches"          # 爬取的比赛数据
PAST_REPORTS_DIR = "Past_Reports"  # LLM 生成的历史报告，供后续 AgentAI 调用
PAST_SCORES_DIR = "Past_Scores"    # 结构化成绩数据，便于查询/对比/做数据库

# 成绩数据的字段（与用户粘贴的列顺序一致）
SCORE_FIELDS = [
    "percent",                    # %：本场完成度百分比
    "points",                     # Pts：得分
    "time",                       # Time：用时（秒）
    "percent_possible",           # % psbl：命中可能得分的百分比
    "division",                   # Div：分区（CO/LO/Limited/Open/PCC 等）
    "class",                      # Class：级别（U/D/C/B/A/M/GM）
    "power_factor",               # PF：动力因子（MAJOR/MINOR）
    "hits_A",                     # A：A 区命中数
    "hits_C",                     # C：C 区命中数
    "hits_D",                     # D：D 区命中数
    "misses_M",                   # M：脱靶数
    "nopenaltymisses_NPM",        # NPM：无罚分脱靶
    "no_shoots_NS",               # NS：误击禁靶
    "procedurals_Proc",           # Proc：程序罚分
    "additional_penalties_Apen",  # Apen：附加罚分
]


def save_output(content: str, base_name: str, ext: str, out_dir: str = MATCHES_DIR) -> str:
    """把内容保存到指定文件夹，文件名加上时间戳。"""
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{ext}"
    save_path = os.path.join(out_dir, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)
    return save_path


def parse_score_line(line: str) -> dict | None:
    """把一行成绩解析为结构化字典。

    列顺序固定为 15 列，各列均为单个 token（division 使用简写如 CO/LO），
    按空格切分后与字段一一对应即可。
    """
    tokens = line.split()
    if len(tokens) < len(SCORE_FIELDS):
        return None
    return dict(zip(SCORE_FIELDS, tokens))


def _read_dir_files(directory: str, extension: str) -> str:
    """读取指定目录下所有某扩展名的文件，返回「文件名 + 内容」的合并文本。"""
    if not os.path.isdir(directory):
        return f"（{directory} 目录不存在或暂无文件）"
    filenames = sorted(f for f in os.listdir(directory) if f.endswith(extension))
    if not filenames:
        return f"（{directory} 目录暂无 {extension} 文件）"
    parts = []
    for name in filenames:
        with open(os.path.join(directory, name), "r", encoding="utf-8") as f:
            parts.append(f"### 文件：{name}\n{f.read()}")
    return "\n\n".join(parts)


@function_tool
def get_past_scores() -> str:
    """读取历史成绩数据（Past_Scores 文件夹中所有 JSON 文件）。

    当你需要把本次成绩与过往成绩做对比、观察进步或退步趋势时调用。
    返回每个历史成绩文件的名称与 JSON 内容。
    """
    return _read_dir_files(PAST_SCORES_DIR, ".json")


@function_tool
def get_past_reports() -> str:
    """读取历史分析报告（Past_Reports 文件夹中所有 Markdown 文件）。

    当你需要参考过往对我的分析结论与训练建议、保持建议连贯时调用。
    返回每个历史报告文件的名称与内容。
    """
    return _read_dir_files(PAST_REPORTS_DIR, ".md")


# Agent 1：比赛规划顾问（只负责参赛日程规划，训练/提升分析交给成绩分析师）
planning_agent = Agent(
    name="Match Planning Coach",
    model="gpt-5",
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
    model="gpt-5",
    tools=[get_past_scores, get_past_reports],
    instructions="""
你是一名资深的射击运动教练与成绩分析师。
我现在是一位C级的USPSA射手，想要升级到B级。
你会收到我的比赛成绩数据（JSON 格式，每个对象是一条成绩，字段名已说明含义）。

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


def run_agent(agent: Agent, data: str) -> str:
    """运行指定 Agent 并返回文本结果。"""
    print("正在调用大模型，请稍候……")
    result = Runner.run_sync(agent, data)

    # 调试输出：统计本次调用了哪些工具、共几次
    tool_calls = [
        item for item in result.new_items
        if item.__class__.__name__ == "ToolCallItem"
    ]
    if tool_calls:
        names = []
        for item in tool_calls:
            raw = getattr(item, "raw_item", None)
            names.append(getattr(raw, "name", "unknown"))
        print(f"[调试] 本次调用工具 {len(tool_calls)} 次：{', '.join(names)}")
    else:
        print("[调试] 本次未调用任何工具")

    return result.final_output


def choose_and_output(saveables: list[tuple], printable: str) -> None:
    """让用户选择输出方式，并按选择保存/打印。

    saveables: 需要保存的内容列表，每项为 (content, base_name, ext, out_dir)。
    printable: 选择打印时要输出到屏幕的文本。
    """
    output_type = input(
        "请选择输出方式（1: 打印到屏幕，2: 保存为文件，3: 同时打印+保存，默认 1）："
    ).strip()

    if output_type in ("2", "3"):
        for content, base_name, ext, out_dir in saveables:
            save_path = save_output(content, base_name, ext, out_dir)
            print(f"已保存到：{save_path}")

    if output_type != "2":
        print(printable)


# 开始阶段选择运行模式
mode = input(
    "请选择运行模式（1: 使用 LLM 生成比赛规划，2: 仅输出爬取的比赛，3: 成绩分析，默认 1）："
).strip()

clubs_path = "Informations/clubs.json"

# 模式 3：成绩分析——用户粘贴成绩数据，解析为 JSON 后交给 LLM 分析
if mode == "3":
    print("列顺序如下：")
    print("%  Pts  Time  % psbl  Div  Class  PF  A  C  D  M  NPM  NS  Proc  Apen")
    print("Div 可用简写：CO / LO / Limited / Open / PCC 等")
    print("示例：42.66% 193.5518 260.40 41.79 CO U MINOR 79 15 2 5 - - - -")
    print("请逐行粘贴成绩数据，全部粘贴完成后，在新的一行输入 END 回车结束：")

    records = []
    while True:
        try:
            line = input()
        except EOFError:  # 防止读到 EOF 时无限阻塞
            break
        if line.strip().upper() == "END":
            break
        if not line.strip():
            continue
        record = parse_score_line(line)
        if record is None:
            print(f"[跳过] 列数不足，无法解析：{line}")
        else:
            records.append(record)

    if not records:
        print("未输入任何有效成绩数据，已退出。")
        raise SystemExit(0)

    scores_json = json.dumps(records, ensure_ascii=False, indent=2)

    # 成绩 JSON 保存到 Past_Scores，方便后续查询/对比/做数据库
    scores_path = save_output(scores_json, "scores", "json", out_dir=PAST_SCORES_DIR)
    print(f"成绩已保存到：{scores_path}")

    # 选择：调用大模型分析，还是仅导出 JSON
    analyze = input(
        "是否调用大模型分析成绩？（1: 是，进行分析，2: 否，仅导出 JSON，默认 1）："
    ).strip()

    if analyze == "2":
        print(scores_json)
        raise SystemExit(0)

    output_text = run_agent(score_agent, f"成绩数据：\n{scores_json}")
    choose_and_output(
        [(output_text, "score_report", "md", PAST_REPORTS_DIR)],
        output_text,
    )

    raise SystemExit(0)

# 模式 2：不使用 LLM，直接输出爬取的比赛
if mode == "2":
    print("正在抓取俱乐部比赛信息，请稍候……")
    results = scrape_all(clubs_path)
    matches_json = json.dumps(results, ensure_ascii=False, indent=2)
    matches_text = format_matches_text(results)

    # JSON 与「交给 LLM 的文本」都保存到 Matches；打印时显示 JSON
    choose_and_output(
        [
            (matches_json, "matches", "json", MATCHES_DIR),
            (matches_text, "matches", "txt", MATCHES_DIR),
        ],
        matches_json,
    )

    raise SystemExit(0)


# 模式 1：使用 LLM 生成比赛规划
# 从俱乐部网站抓取即将进行的比赛
print("正在抓取俱乐部比赛信息，请稍候……")
document = get_upcoming_matches_text(clubs_path)

output_text = run_agent(planning_agent, f"比赛信息：\n{document}")
choose_and_output(
    [(output_text, "report", "md", PAST_REPORTS_DIR)],
    output_text,
)
