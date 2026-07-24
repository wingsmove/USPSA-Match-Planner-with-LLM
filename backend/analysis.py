"""把数据库里的成绩交给 LLMs 的成绩分析 Agent 生成报告。

LLMs 相关代码在 backend/LLMs/ 下，这里把该目录加入 import 搜索路径后复用其中的
score_agent 和 run_agent，避免重复实现。
"""

import json
import os
import sys

from sqlalchemy.orm import Session

import models

# 让 backend/LLMs 下的模块可被导入。
# 用 append（加到末尾）而不是 insert(0)，避免 LLMs/main.py 等与后端同名模块冲突。
_LLMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LLMs")
if _LLMS_DIR not in sys.path:
    sys.path.append(_LLMS_DIR)

# 加载仓库根目录的 .env，确保 OPENAI_API_KEY 可用
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(_REPO_ROOT, ".env"))
except ImportError:
    pass

from coach_agents import run_agent, score_agent, planning_agent  # noqa: E402  (需在 sys.path 设置后导入)
from scraper import format_matches_text, scrape_clubs  # noqa: E402  (需在 sys.path 设置后导入)

# 交给 LLM 的字段（数据库列名）
_FIELDS = [
    "percent", "points", "time", "percent_possible", "division",
    "shooter_class", "power_factor", "hits_a", "hits_c", "hits_d", "misses_m",
    "nopenaltymisses_npm", "no_shoots", "procedurals", "additional_penalties_apen",
]

def analyze_db_scores(db: Session) -> str:
    """读取数据库全部成绩，转成 JSON 交给成绩分析 Agent，返回分析报告文本。"""
    rows = db.query(models.Score).order_by(models.Score.id).all()
    records = [{field: getattr(row, field) for field in _FIELDS} for row in rows]
    scores_json = json.dumps(records, ensure_ascii=False, indent=2)
    report = run_agent(score_agent, f"成绩数据：\n{scores_json}")
    db.add(models.AnalysisReport(content=report))
    db.commit()
    return report

def plan_matches(db: Session) -> str:
    """从数据库读取俱乐部，爬取各俱乐部即将进行的比赛，转成 JSON 交给比赛规划 Agent。"""
    rows = db.query(models.Club).order_by(models.Club.id).all()
    # 数据库俱乐部 -> scraper 需要的 {name, url} 格式
    clubs = [{"name": row.club_name, "url": row.club_url} for row in rows]
    # 复用 LLMs 里的 scraper：抓取比赛，并用原有的 format_matches_text 格式化
    results = scrape_clubs(clubs)
    matches_text = format_matches_text(results)
    return run_agent(planning_agent, f"比赛信息：\n{matches_text}")
