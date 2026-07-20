"""文件保存、成绩数据库读写等存储相关工具。"""

import json
import os
from datetime import datetime

from config import MATCHES_DIR, PAST_SCORES_DIR, SCORES_DB_PATH


def save_output(content: str, base_name: str, ext: str, out_dir: str = MATCHES_DIR) -> str:
    """把内容保存到指定文件夹，文件名加上时间戳。"""
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{ext}"
    save_path = os.path.join(out_dir, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)
    return save_path


def append_scores_to_db(records: list[dict]) -> str:
    """把本次导入的成绩追加写入 JSON 数据库文件，返回数据库路径。

    每条记录附带 imported_at（导入时间）以区分不同批次。
    """
    os.makedirs(PAST_SCORES_DIR, exist_ok=True)

    # 读取已有数据库（文件损坏时以空库重来，避免直接崩溃）
    db = []
    if os.path.exists(SCORES_DB_PATH):
        try:
            with open(SCORES_DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            if not isinstance(db, list):
                db = []
        except (json.JSONDecodeError, OSError):
            print(f"[警告] {SCORES_DB_PATH} 无法读取，将新建数据库。")
            db = []

    imported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for record in records:
        db.append({"imported_at": imported_at, **record})

    with open(SCORES_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    return SCORES_DB_PATH


def read_dir_files(directory: str, extension: str) -> str:
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
