"""成绩数据的 JSON <-> 数据库 一键导入/导出。

- 导入：把 LLM 侧生成的成绩 JSON（Past_Scores/scores_db.json）写入数据库。
- 导出：把数据库里的所有成绩导出成一个 JSON 文件。

注意：LLM 侧 JSON 的字段名与数据库列名不完全一致（如 class→shooter_class、
hits_A→hits_a、用 "-" 表示 0），因此导入时做键映射 + 值转换。
"""

import json
import os
from datetime import datetime

from sqlalchemy.orm import Session

import models

# 仓库根目录：本文件在 <root>/backend/import_export.py，向上两层即根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAST_SCORES_DIR = os.path.join(BASE_DIR, "Past_Scores")
DEFAULT_IMPORT_PATH = os.path.join(PAST_SCORES_DIR, "scores_db.json")

# LLM 侧 JSON 字段名 -> 数据库列名
JSON_TO_DB = {
    "percent": "percent",
    "points": "points",
    "time": "time",
    "percent_possible": "percent_possible",
    "division": "division",
    "class": "shooter_class",
    "power_factor": "power_factor",
    "hits_A": "hits_a",
    "hits_C": "hits_c",
    "hits_D": "hits_d",
    "misses_M": "misses_m",
    "nopenaltymisses_NPM": "nopenaltymisses_npm",
    "no_shoots_NS": "no_shoots",
    "procedurals_Proc": "procedurals",
    "additional_penalties_Apen": "additional_penalties_apen",
}

# 数据库里是整数类型的列
INT_COLUMNS = {
    "hits_a", "hits_c", "hits_d", "misses_m",
    "no_shoots", "nopenaltymisses_npm", "procedurals", "additional_penalties_apen",
}

# 导出时输出的所有列（含 id 与 created_at）
EXPORT_COLUMNS = [
    "id", "percent", "points", "time", "percent_possible", "division",
    "shooter_class", "power_factor", "hits_a", "hits_c", "hits_d", "misses_m",
    "nopenaltymisses_npm", "no_shoots", "procedurals", "additional_penalties_apen",
    "created_at",
]


def _to_int(value) -> int:
    """把 JSON 里的数字字段转成整数；"-"、空、None、非法值都当 0。"""
    if value is None:
        return 0
    text = str(value).strip()
    if text in ("", "-"):
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def import_json_to_db(db: Session, json_path: str = DEFAULT_IMPORT_PATH) -> int:
    """把 JSON 文件里的成绩逐条写入数据库，返回导入条数。"""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"找不到 JSON 文件：{json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    count = 0
    for rec in records:
        data = {}
        for json_key, column in JSON_TO_DB.items():
            value = rec.get(json_key)
            if column in INT_COLUMNS:
                data[column] = _to_int(value)
            else:
                data[column] = value if value is not None else ""
        db.add(models.Score(**data))
        count += 1

    db.commit()
    return count


def export_db_to_json(db: Session, out_dir: str = PAST_SCORES_DIR) -> tuple[int, str]:
    """把数据库里所有成绩导出为一个带时间戳的 JSON 文件，返回 (条数, 路径)。"""
    os.makedirs(out_dir, exist_ok=True)
    rows = db.query(models.Score).order_by(models.Score.id).all()

    data = []
    for row in rows:
        item = {}
        for column in EXPORT_COLUMNS:
            value = getattr(row, column)
            # created_at 是 datetime，转成字符串才能写进 JSON
            if isinstance(value, datetime):
                value = value.isoformat()
            item[column] = value
        data.append(item)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"db_export_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data), out_path
