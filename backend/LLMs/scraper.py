import json
import re

import cloudscraper
from bs4 import BeautifulSoup

from config import CLUBS_PATH

#读取俱乐部列表
def load_clubs(path: str = CLUBS_PATH) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

#抓取页面 HTML
def fetch_html(url: str, timeout: int = 60) -> str:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text

#清理文本
def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

#解析即将进行的比赛
def parse_upcoming_matches(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    matches = []

    for item in soup.select('div[id^="item_"]'):
        # 名称
        strong = item.find("strong")
        name = _clean(strong.get_text()) if strong else ""

        # 报名/详情链接
        link = strong.find("a") if strong else None
        match_url = link["href"] if link and link.has_attr("href") else ""

        # 状态标签
        label = item.select_one("span.label")
        status = _clean(label.get_text()) if label else ""

        # 日期与项目：small 内的 div，第一个是日期，其余是项目/级别
        date = ""
        discipline = ""
        small = item.find("small")
        if small:
            divs = small.find_all("div")
            if len(divs) >= 1:
                date = _clean(divs[0].get_text()).rstrip("·").strip()
            if len(divs) >= 2:
                discipline = _clean(divs[1].get_text())

        # 只保留 USPSA / IPSC 的比赛，排除其他项目
        discipline_upper = discipline.upper()
        is_uspsa_or_ipsc = "USPSA" in discipline_upper or "IPSC" in discipline_upper

        if name and is_uspsa_or_ipsc:
            matches.append(
                {
                    "name": name,
                    "date": date,
                    "discipline": discipline,
                    "status": status,
                    "url": match_url,
                }
            )

    return matches

#抓取单个俱乐部的即将进行的比赛
def scrape_club(club: dict) -> dict:
    html = fetch_html(club["url"])
    matches = parse_upcoming_matches(html)
    return {"name": club.get("name", ""), "url": club["url"], "matches": matches}

#抓取给定俱乐部列表的即将进行的比赛（俱乐部可来自文件，也可来自数据库）
def scrape_clubs(clubs: list[dict]) -> list[dict]:
    results = []
    for club in clubs:
        try:
            results.append(scrape_club(club))
        except Exception as exc:  # 单个俱乐部失败不影响其余
            print(f"[警告] 抓取失败 {club.get('name', club.get('url'))}: {exc}")
    return results

#抓取所有俱乐部的即将进行的比赛（从 clubs.json 读取俱乐部列表）
def scrape_all(path: str = CLUBS_PATH) -> list[dict]:
    return scrape_clubs(load_clubs(path))

#格式化比赛文本
def format_matches_text(results: list[dict]) -> str:
    lines = []
    for club in results:
        lines.append(f"# 俱乐部：{club['name']}")
        lines.append(f"网址：{club['url']}")
        if not club["matches"]:
            lines.append("（未找到即将进行的比赛）")
            lines.append("")
            continue
        lines.append(f"即将进行的比赛（共 {len(club['matches'])} 场）：")
        for i, m in enumerate(club["matches"], start=1):
            lines.append(
                f"{i}. {m['name']}\n"
                f"   - 日期：{m['date'] or '未知'}\n"
                f"   - 项目：{m['discipline'] or '未知'}\n"
                f"   - 状态：{m['status'] or '未知'}\n"
                f"   - 链接：{m['url'] or '无'}"
            )
        lines.append("")
    return "\n".join(lines)


def get_upcoming_matches_text(path: str = CLUBS_PATH) -> str:
    return format_matches_text(scrape_all(path))


if __name__ == "__main__":
    print(get_upcoming_matches_text())
