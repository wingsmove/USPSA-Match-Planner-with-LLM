import json

from dotenv import load_dotenv

from coach_agents import planning_agent, run_agent, score_agent
from config import CLUBS_PATH, MATCHES_DIR, PAST_REPORTS_DIR
from scores import read_scores_from_input
from scraper import format_matches_text, get_upcoming_matches_text, scrape_all
from storage import append_scores_to_db, save_output

load_dotenv()

#选择输出方式
def choose_and_output(saveables: list[tuple], printable: str) -> None:
    output_type = input(
        "请选择输出方式（1: 打印到屏幕，2: 保存为文件，3: 同时打印+保存，默认 1）："
    ).strip()

    if output_type in ("2", "3"):
        for content, base_name, ext, out_dir in saveables:
            save_path = save_output(content, base_name, ext, out_dir)
            print(f"已保存到：{save_path}")

    if output_type != "2":
        print(printable)


#录入成绩 -> 写入数据库 -> （可选）交给成绩分析 Agent
def run_score_analysis() -> None:
    records = read_scores_from_input()
    if not records:
        print("未输入任何有效成绩数据，已退出。")
        return

    scores_json = json.dumps(records, ensure_ascii=False, indent=2)

    # 追加写入 JSON 数据库，作为累积成绩的临时数据库，方便后续查询/对比
    db_path = append_scores_to_db(records)
    print(f"本次 {len(records)} 条成绩已写入数据库：{db_path}")

    analyze = input(
        "是否调用大模型分析成绩？（1: 是，进行分析，2: 否，仅导出 JSON，默认 1）："
    ).strip()
    if analyze == "2":
        print(scores_json)
        return

    output_text = run_agent(score_agent, f"成绩数据：\n{scores_json}")
    choose_and_output(
        [(output_text, "score_report", "md", PAST_REPORTS_DIR)],
        output_text,
    )

#抓取比赛并直接导出
def run_match_export() -> None:
    print("正在抓取俱乐部比赛信息，请稍候……")
    results = scrape_all(CLUBS_PATH)
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

#抓取比赛并交给比赛规划 Agent 生成日程规划
def run_match_planning() -> None:
    print("正在抓取俱乐部比赛信息，请稍候……")
    document = get_upcoming_matches_text(CLUBS_PATH)

    output_text = run_agent(planning_agent, f"比赛信息：\n{document}")
    choose_and_output(
        [(output_text, "report", "md", PAST_REPORTS_DIR)],
        output_text,
    )


def main() -> None:
    mode = input(
        "请选择运行模式（1: 使用 LLM 生成比赛规划，2: 仅输出爬取的比赛，3: 成绩分析，默认 1）："
    ).strip()

    if mode == "3":
        run_score_analysis()
    elif mode == "2":
        run_match_export()
    else:
        run_match_planning()


if __name__ == "__main__":
    main()
