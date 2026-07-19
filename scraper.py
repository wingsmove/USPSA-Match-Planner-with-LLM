"""爬取 clubs.json 中俱乐部页面的 "Upcoming Matches" 信息。

目标站点 practiscore.com 使用 Cloudflare 防护，普通请求会返回 403，
因此这里使用 cloudscraper 绕过 "Just a moment..." 挑战，再用 BeautifulSoup 解析。
"""

import json
import re

import cloudscraper
from bs4 import BeautifulSoup


def load_clubs(path: str = "clubs.json") -> list[dict]:
    """读取俱乐部列表。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_html(url: str, timeout: int = 60) -> str:
    """抓取页面 HTML（自动处理 Cloudflare 挑战）。"""
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def _clean(text: str) -> str:
    """把多余空白折叠成单个空格。"""
    return re.sub(r"\s+", " ", text).strip()


def parse_upcoming_matches(html: str) -> list[dict]:
    """从俱乐部页面 HTML 中解析出即将进行的比赛。

    每场比赛对应一个 <div class="clearfix" id="item_XXXX">，包含：
      - 状态标签 (span.label)：如 open / Private: opens in 2 weeks
      - 名称 (strong)：可能是链接，也可能是纯文本（如 Private Match）
      - 日期与项目 (small 内的两个 div)
    """
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


def scrape_club(club: dict) -> dict:
    """抓取单个俱乐部的即将进行的比赛。"""
    html = fetch_html(club["url"])
    matches = parse_upcoming_matches(html)
    return {"name": club.get("name", ""), "url": club["url"], "matches": matches}


def scrape_all(path: str = "clubs.json") -> list[dict]:
    """抓取 clubs.json 中所有俱乐部。"""
    results = []
    for club in load_clubs(path):
        try:
            results.append(scrape_club(club))
        except Exception as exc:  # 单个俱乐部失败不影响其余
            print(f"[警告] 抓取失败 {club.get('name', club.get('url'))}: {exc}")
    return results


def format_matches_text(results: list[dict]) -> str:
    """把抓取结果格式化为纯文本，供大模型阅读。"""
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


def get_upcoming_matches_text(path: str = "clubs.json") -> str:
    """对外主入口：抓取并返回格式化后的比赛文本。"""
    return format_matches_text(scrape_all(path))


if __name__ == "__main__":
    print(get_upcoming_matches_text())
