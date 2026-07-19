# USPSA-Match-Planner-with-LLM
一个 LLM / Agent AI 的实践项目：自动爬取 [PractiScore](https://practiscore.com) 俱乐部页面的「即将进行的比赛」信息，交给大模型（OpenAI GPT）为射手生成**比赛规划与训练安排**。

## 功能简介

- **爬虫（`scraper.py`）**：读取 `Informations/clubs.json` 中的俱乐部列表，抓取每个俱乐部页面的 *Upcoming Matches*，解析出比赛名称、日期、项目/级别、报名状态与链接。使用 `cloudscraper`爬取，再用 `BeautifulSoup` 解析。
- **规划助手（`main.py`）**：把抓取到的比赛信息组织成提示词，调用 OpenAI 模型，以射击教练的视角生成参赛建议、阶段性训练计划、备赛重点、报名提醒等，并以 Markdown 输出。
- **两种运行模式**：启动时可选择「使用 LLM 生成比赛规划」或「仅输出爬取的比赛」（不调用 LLM，也就无需 API Key）。
- **归档输出**：所有保存的输出文件名自动带时间戳，避免覆盖历史结果。爬取数据存入 `Matches/`，LLM 生成的报告存入 `Past_Reports/`（方便后续 AgentAI 调用历史报告作为上下文）。

## 目录结构

```
.
├── main.py            # 主程序：选择模式 -> 抓取比赛 -> 输出规划或原始数据
├── scraper.py         # 爬虫模块：抓取并解析 Upcoming Matches
├── Informations/
│   └── clubs.json     # 俱乐部列表（name + url）
├── requirements.txt   # 依赖
├── Matches/           # 爬取数据输出目录（自动生成，已被 .gitignore 忽略）
├── Past_Reports/      # LLM 报告归档目录（自动生成，已被 .gitignore 忽略）
└── .env               # 环境变量（需自行创建，见下）
```

## 环境要求

- Python 3.10+
- 一个有效的 OpenAI API Key

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

### 1. 配置俱乐部列表

编辑 `Informations/clubs.json`，填入想要跟踪的 PractiScore 俱乐部（`name` 为显示名称，`url` 为俱乐部主页地址）：

```json
[
  {
    "name": "Club Name",
    "url": "https://practiscore.com/clubs/club_name"
  }
]
```

### 2. 运行主程序

```bash
python main.py
```

程序启动时会先询问**运行模式**：

#### 模式 1：使用 LLM 生成比赛规划（默认）

1. 抓取 `Informations/clubs.json` 中所有俱乐部的即将进行的比赛；
2. 调用大模型生成比赛规划与训练安排；
3. 询问输出方式：
   - `1`（默认）：打印到屏幕
   - `2`：保存为 Markdown 文件
   - `3`：同时打印并保存
4. 保存的报告位于 `Past_Reports/report_<时间戳>.md`，供后续 AgentAI 调用。

#### 模式 2：仅输出爬取的比赛（不调用 LLM）

1. 抓取并解析所有俱乐部的即将进行的比赛；
2. 询问输出方式（打印 / 保存 / 两者）；
3. 保存时会**同时**生成两份带时间戳的文件到 `Matches/`：
   - `matches_<时间戳>.json`：结构化 JSON 数据
   - `matches_<时间戳>.txt`：与交给 LLM 相同的格式化文本
4. 此模式不调用 OpenAI，因此无需配置 API Key。

### 3. 单独运行爬虫（可选）

只想查看抓取结果、不调用大模型时：

```bash
python scraper.py
```

## 说明

- 输出均带时间戳：爬取数据保存在 `Matches/`，LLM 报告保存在 `Past_Reports/`；两个目录都已加入 `.gitignore`，不会被提交。
- `Past_Reports/` 中的历史报告可作为后续 AgentAI 开发时的上下文数据来源。
- 当前 `main.py` 的提示词假设使用者是一名希望从 **C 级升到 B 级** 的 USPSA 射手，可根据自身情况在 `main.py` 中调整提示词。

## 依赖

主要依赖：`openai`、`python-dotenv`、`cloudscraper`、`beautifulsoup4`（完整列表见 `requirements.txt`）。
