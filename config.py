#集中管理项目的路径、模型等配置常量

import os

# 输出目录
MATCHES_DIR = "Matches"          # 爬取的比赛数据
PAST_REPORTS_DIR = "Past_Reports"  # LLM 生成的历史报告，供后续 AgentAI 调用
PAST_SCORES_DIR = "Past_Scores"    # 结构化成绩数据，便于查询/对比/做数据库

# 累积所有成绩的 JSON 数据库
SCORES_DB_PATH = os.path.join(PAST_SCORES_DIR, "scores_db.json")

# 俱乐部列表
CLUBS_PATH = "Informations/clubs.json"

# 使用的大模型
MODEL = "gpt-5"

# 成绩数据的字段（与用户粘贴的列顺序一致）
SCORE_FIELDS = [
    "percent",                    # %：本场完成度百分比
    "points",                     # Pts：得分
    "time",                       # Time：用时（秒）
    "percent_possible",           # % psbl：命中可能得分的百分比
    "division",                   # Div：分区（CO/LO/Limited/Open/PCC等）
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
