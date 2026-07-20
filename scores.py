"""成绩数据的解析与交互式录入。"""

from config import SCORE_FIELDS


def parse_score_line(line: str) -> dict | None:
    """把一行成绩解析为结构化字典。

    列顺序固定为 15 列，各列均为单个 token（division 使用简写如 CO/LO），
    按空格切分后与字段一一对应即可。
    """
    tokens = line.split()
    if len(tokens) < len(SCORE_FIELDS):
        return None
    return dict(zip(SCORE_FIELDS, tokens))


def read_scores_from_input() -> list[dict]:
    """提示并逐行读取用户粘贴的成绩，解析为结构化记录列表。"""
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
    return records
