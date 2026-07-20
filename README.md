# USPSA-Match-Planner-with-LLM

一个基于 **OpenAI Agents SDK** 的实践项目：自动爬取 [PractiScore](https://practiscore.com) 俱乐部页面的「即将进行的比赛」信息，并用不同的 AI Agent 为射手生成**比赛规划**与**成绩分析**。

## 功能简介

- **爬虫（`scraper.py`）**：读取 `Informations/clubs.json` 中的俱乐部列表，抓取每个俱乐部页面公开展示的 *Upcoming Matches*，解析出比赛名称、日期、项目/级别、报名状态与链接（仅保留 USPSA / IPSC 比赛）。使用 `cloudscraper` + `BeautifulSoup` 抓取并解析页面。
- **两个 AI Agent（`main.py`）**：
  - **比赛规划 Agent**（`planning_agent`）：只负责参赛日程规划——梳理比赛时间线、给出参赛建议、报名提醒与链接。
  - **成绩分析 Agent**（`score_agent`）：负责训练与提升的深入分析——总体评价、失分点、升级重点、阶段性训练计划、备赛重点。该 Agent 挂载了两个工具，可由模型**自行决定是否调用**：
    - `get_past_scores`：读取历史成绩（`Past_Scores/`），做纵向对比、判断趋势。
    - `get_past_reports`：读取历史报告（`Past_Reports/`），保持建议连贯。
- **结构化成绩存储**：成绩分析模式下，用户粘贴的成绩会被解析为结构化 JSON 存入 `Past_Scores/`，便于后续查询、对比或做成数据库。
- **归档输出**：所有保存的输出文件名自动带时间戳，避免覆盖历史结果。

## 目录结构

```
.
├── main.py            # 主程序：选择模式 -> 抓取/输入 -> Agent 分析 -> 输出
├── scraper.py         # 爬虫模块：抓取并解析 Upcoming Matches
├── Informations/
│   └── clubs.json     # 俱乐部列表（name + url）
├── requirements.txt   # 依赖
├── Matches/           # 爬取数据输出目录（自动生成，已被 .gitignore 忽略）
├── Past_Scores/       # 结构化成绩 JSON 目录（自动生成，已被 .gitignore 忽略）
├── Past_Reports/      # LLM 报告归档目录（自动生成，已被 .gitignore 忽略）
└── .env               # 环境变量（需自行创建，见下）
```

## 环境要求

- Python 3.10+
- 一个有效的 OpenAI API Key（模式 2 纯爬取除外）

## 安装

```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件，写入你的 OpenAI API Key：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

## 使用方法

编辑 `Informations/clubs.json`，填入想要跟踪的 PractiScore 俱乐部：

```json
[
  {
    "name": "Club Name",
    "url": "https://practiscore.com/clubs/club_name"
  }
]
```

然后运行主程序：

```bash
python main.py
```

启动时会先选择**运行模式**：

### 模式 1：使用 LLM 生成比赛规划（默认）

1. 抓取 `Informations/clubs.json` 中所有俱乐部的即将进行的比赛；
2. 由 `planning_agent` 生成参赛日程规划；
3. 选择输出方式（打印 / 保存 / 两者），报告保存到 `Past_Reports/report_<时间戳>.md`。

### 模式 2：仅输出爬取的比赛（不调用 LLM）

1. 抓取并解析所有俱乐部的即将进行的比赛（只抓取一次，复用数据）；
2. 选择输出方式；保存时同时生成两份文件到 `Matches/`：
   - `matches_<时间戳>.json`：结构化 JSON 数据
   - `matches_<时间戳>.txt`：与交给 LLM 相同的格式化文本
3. 此模式不调用 OpenAI，无需配置 API Key。

### 模式 3：成绩分析

1. 按提示逐行粘贴成绩数据，列顺序如下（`Div` 用简写 CO / LO / Limited / Open / PCC 等），全部粘贴完成后在新行输入 `END` 结束：

   ```
   %  Pts  Time  % psbl  Div  Class  PF  A  C  D  M  NPM  NS  Proc  Apen
   示例：42.66% 193.5518 260.40 41.79 CO U MINOR 79 15 2 5 - - - -
   ```

2. 成绩会被解析为结构化 JSON 并保存到 `Past_Scores/scores_<时间戳>.json`；
3. 询问是否调用大模型：
   - `2`：仅导出 JSON（不调用 LLM）；
   - `1`（默认）：由 `score_agent` 进行成绩分析，期间模型可自行调用工具读取历史成绩/报告做对比；
4. 选择输出方式，分析报告保存到 `Past_Reports/score_report_<时间戳>.md`。

> 运行时终端会打印 `[调试]` 信息，显示本次 Agent 是否调用了工具及调用次数。

### 单独运行爬虫（可选）

只想查看抓取结果、不调用大模型时：

```bash
python scraper.py
```

## 说明

- 输出均带时间戳：爬取数据在 `Matches/`，结构化成绩在 `Past_Scores/`，LLM 报告在 `Past_Reports/`。
- 上述三个输出目录以及 `.env`、`*.txt`、`*.pdf` 等均已在 `.gitignore` 中忽略，不会被提交（其中含个人成绩与密钥，请勿手动加入版本库）。
- `Past_Scores/` 的历史成绩与 `Past_Reports/` 的历史报告，会作为成绩分析 Agent 工具的数据来源，用于纵向对比与延续建议。
- 当前 Agent 的指令假设使用者是一名希望从 **C 级升到 B 级** 的 USPSA 射手，可在 `main.py` 中调整各 Agent 的 `instructions`。

## 使用须知

- 本项目仅用于个人学习与研究，抓取的是网站上公开可见的比赛信息。
- 请自行遵守目标网站的服务条款（Terms of Service）与 `robots.txt`，控制请求频率，避免对站点造成压力或用于商业用途。
- 数据的时效性与准确性以网站原始页面为准，本项目不对抓取结果作任何担保。

## 依赖

主要依赖：`openai-agents`（Agents SDK）、`openai`、`python-dotenv`、`cloudscraper`、`beautifulsoup4`（完整列表见 `requirements.txt`）。
