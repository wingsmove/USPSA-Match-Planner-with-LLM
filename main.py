import json
import os
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from scraper import format_matches_text, get_upcoming_matches_text, scrape_all

load_dotenv()

OUTPUT_DIR = "Matches"


def save_output(content: str, base_name: str, ext: str) -> str:
    """把内容保存到 Matches 文件夹，文件名加上时间戳。"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{ext}"
    save_path = os.path.join(OUTPUT_DIR, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)
    return save_path


# 开始阶段选择运行模式：是否使用 LLM
mode = input(
    "请选择运行模式（1: 使用 LLM 生成比赛规划，2: 仅输出爬取的比赛，默认 1）："
).strip()

clubs_path = "clubs.json"

# 模式 2：不使用 LLM，直接输出爬取的比赛
if mode == "2":
    print("正在抓取俱乐部比赛信息，请稍候……")
    results = scrape_all(clubs_path)
    matches_json = json.dumps(results, ensure_ascii=False, indent=2)
    matches_text = format_matches_text(results)

    output_type = input(
        "请选择输出方式（1: 打印到屏幕，2: 保存为文件，3: 同时打印+保存，默认 1）："
    ).strip()

    if output_type in ("2", "3"):
        # JSON 与「交给 LLM 的文本」都保存到 Matches，文件名带时间戳
        json_path = save_output(matches_json, "matches", "json")
        txt_path = save_output(matches_text, "matches", "txt")
        print(f"已保存到：{json_path}")
        print(f"已保存到：{txt_path}")

    if output_type != "2":
        print(matches_json)

    raise SystemExit(0)


# 模式 1：使用 LLM 生成比赛规划
client = OpenAI()

# 从俱乐部网站抓取即将进行的比赛
print("正在抓取俱乐部比赛信息，请稍候……")
document = get_upcoming_matches_text(clubs_path)

prompt = f"""
你是一名资深的射击运动教练与赛事规划顾问。
你正在帮助我制定未来的比赛规划与训练安排。
我现在是一位C级的USPSA射手，想要升级到B级。
下面是从俱乐部网站抓取到的「即将进行的比赛」信息。
请根据这些比赛，为我制定未来的比赛规划与训练安排。

要求：
1. 按时间顺序梳理即将进行的比赛，标注日期、项目与级别
2. 给出参赛建议：哪些比赛值得重点准备、哪些可作为练习赛
3. 制定一份从现在到各场比赛之间的阶段性训练计划（分周或分阶段）
4. 针对不同级别（如 level I / level II）的比赛给出针对性的准备重点
5. 提示报名状态（如尚未开放报名）等需要注意的事项
6. 如果比赛时间与我的训练时间冲突，请给出调整建议
7. 请给出报名链接，截止时间在此页面看不到，就不需要提示了
8. 不要编造比赛信息中没有的内容

必须以 markdown 格式输出。
比赛信息：
{document}
"""

response = client.responses.create(
    model="gpt-5",
    input=prompt
)

output_text = response.output_text

# 选择输出方式：Print，保存为 txt，或都要
output_type = input(
    "请选择输出方式（1: 打印到屏幕，2: 保存为 Markdown，3: 同时打印+保存，默认 1）："
).strip()

if output_type in ("2", "3"):
    save_path = save_output(output_text, "report_output", "md")
    print(f"已保存到：{save_path}")

if output_type != "2":
    print(output_text)
