"""ORM 模型：用 Python 类描述数据库表结构。

每个类 = 一张表，每个 Column = 一个字段。
SQLAlchemy 会据此在数据库里创建对应的表。
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from database import Base


class Score(Base):
    """一条 USPSA 比赛成绩（对应数据库表 scores）。"""

    __tablename__ = "scores"

    # 主键：每行唯一的 id，自增
    id = Column(Integer, primary_key=True, index=True)

    # 成绩字段（与项目里成绩 JSON 的字段对应）
    percent = Column(String)              # 完成度百分比，如 "48.32%"
    points = Column(String)              # 得分
    time = Column(String)                # 用时（秒）
    percent_possible = Column(String)    # 命中可能得分的百分比
    division = Column(String)            # 分区（CO/LO/Limited/Open/PCC）
    shooter_class = Column(String)       # 级别（U/D/C/B/A/M/GM）；class 是关键字故改名
    power_factor = Column(String)        # 动力因子（MAJOR/MINOR）
    hits_a = Column(Integer)             # A 区命中数
    hits_c = Column(Integer)             # C 区命中数
    hits_d = Column(Integer)             # D 区命中数
    misses_m = Column(Integer)           # 脱靶数
    nopenaltymisses_npm = Column(Integer) # 无罚脱靶数
    no_shoots = Column(Integer)         # 误击禁靶数
    procedurals = Column(Integer)        # 程序罚分数
    additional_penalties_apen = Column(Integer) # 额外罚分数

    # 创建时间：由数据库在插入时自动填当前时间
    created_at = Column(DateTime, server_default=func.now())

class Club(Base):
    """一个 USPSA 俱乐部（对应数据库表 clubs）。"""

    __tablename__ = "clubs"

    # 主键：每行唯一的 id，自增
    id = Column(Integer, primary_key=True, index=True)

    # 俱乐部字段（与项目里俱乐部 JSON 的字段对应）
    club_name = Column(String)         # 俱乐部名称
    club_url = Column(String)          # 俱乐部 URL


class AnalysisReport(Base):
    """一份由 LLM 生成的成绩分析报告。"""

    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
