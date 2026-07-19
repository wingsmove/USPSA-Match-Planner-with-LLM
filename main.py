from openai import OpenAI
from dotenv import load_dotenv

from scraper import get_upcoming_matches_text

load_dotenv()

client = OpenAI()


# 从俱乐部网站抓取即将进行的比赛
clubs_path = "clubs.json"
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
5. 提示报名截止、状态（如尚未开放报名）等需要注意的事项
6. 如果比赛时间与我的训练时间冲突，请给出调整建议
7. 请给出报名截止时间，以及报名链接
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
    "请选择输出方式（1: 打印到屏幕，2: 保存为 txt，3: 同时打印+保存，默认 1）："
).strip()

if output_type in ("2", "3"):
    save_path = input("请输入保存的 txt 文件路径（默认 report_output.txt）：").strip()
    if not save_path:
        save_path = "report_output.txt"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"已保存到：{save_path}")

if output_type != "2":
    print(output_text)
