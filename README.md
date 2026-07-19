# LLM-AgentAI-Development-Test

一个 LLM / Agent AI 的实践项目：自动爬取 [PractiScore](https://practiscore.com) 俱乐部页面的「即将进行的比赛」信息，交给大模型（OpenAI GPT）为射手生成**比赛规划与训练安排**。

## 功能简介

- **爬虫（`scraper.py`）**：读取 `clubs.json` 中的俱乐部列表，抓取每个俱乐部页面的 *Upcoming Matches*，解析出比赛名称、日期、项目/级别、报名状态与链接。目标站点使用 Cloudflare 防护，因此使用 `cloudscraper` 绕过 "Just a moment..."，再用 `BeautifulSoup` 解析。
- **规划助手（`main.py`）**：把抓取到的比赛信息组织成提示词，调用 OpenAI 模型，以射击教练的视角生成参赛建议、阶段性训练计划、备赛重点、报名提醒等，并以 Markdown 输出。

## 目录结构

```
.
├── main.py            # 主程序：抓取比赛 -> 调用大模型 -> 输出规划
├── scraper.py         # 爬虫模块：抓取并解析 Upcoming Matches
├── clubs.json         # 俱乐部列表（name + url）
├── requirements.txt   # 依赖
├── report_output.txt  # 示例输出（可选）
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

编辑 `clubs.json`，填入想要跟踪的 PractiScore 俱乐部（`name` 为显示名称，`url` 为俱乐部主页地址）：

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

程序会：

1. 抓取 `clubs.json` 中所有俱乐部的即将进行的比赛；
2. 调用大模型生成比赛规划与训练安排；
3. 询问输出方式：
   - `1`（默认）：打印到屏幕
   - `2`：保存为 txt 文件（默认 `report_output.txt`）
   - `3`：同时打印并保存

### 3. 单独运行爬虫（可选）

只想查看抓取结果、不调用大模型时：

```bash
python scraper.py
```

## 说明

- 比赛信息完全来自实时抓取，提示词中已要求模型不要编造未出现的内容。
- 当前 `main.py` 的提示词假设使用者是一名希望从 **C 级升到 B 级** 的 USPSA 射手，可根据自身情况在 `main.py` 中调整提示词。

## 依赖

主要依赖：`openai`、`python-dotenv`、`cloudscraper`、`beautifulsoup4`（完整列表见 `requirements.txt`）。
