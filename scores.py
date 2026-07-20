#成绩数据的解析与录入

from config import SCORE_FIELDS

#解析成绩
def parse_score_line(line: str) -> dict | None:
    tokens = line.split()
    if len(tokens) < len(SCORE_FIELDS):
        return None
    return dict(zip(SCORE_FIELDS, tokens))

#录入成绩
def read_scores_from_input() -> list[dict]:
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
