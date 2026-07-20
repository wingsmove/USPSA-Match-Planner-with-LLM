# USPSA-Match-Planner-with-LLM

一个 **全栈 + AI Agent** 的实践项目：为 USPSA 射手提供成绩管理与俱乐部管理，并用 AI 教练（基于 **OpenAI Agents SDK**）生成**成绩分析**与**比赛规划**。

- **前端**：React + TypeScript（Vite）——成绩看板、俱乐部看板。
- **后端**：FastAPI + SQLAlchemy + SQLite——提供 REST API 与数据库。
- **AI 核心（`backend/LLMs/`）**：爬取 [PractiScore](https://practiscore.com) 的即将进行的比赛，并用两个 Agent 生成规划与分析。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 19、TypeScript、Vite |
| 后端 | FastAPI、Uvicorn、SQLAlchemy、SQLite |
| AI | OpenAI Agents SDK（`openai-agents`）、gpt-5 |
| 爬虫 | cloudscraper、BeautifulSoup |

## 目录结构

```
.
├── backend/                 # 后端（FastAPI + SQLite）
│   ├── main.py              # API 入口：/scores、/clubs、/analyze、/plan、导入导出
│   ├── database.py          # SQLAlchemy 引擎与会话（SQLite: app.db）
│   ├── models.py            # ORM 模型：Score、Club
│   ├── schemas.py           # Pydantic 输入/输出模型
│   ├── import_export.py     # 成绩 JSON <-> 数据库 一键导入/导出
│   ├── analysis.py          # 桥接 LLMs：成绩分析 / 比赛规划
│   ├── app.db               # SQLite 数据库（自动生成，已被忽略）
│   ├── requirements.txt     # 后端依赖
│   └── LLMs/                # AI 核心（爬虫 + Agent，也可单独作为 CLI 运行）
│       ├── scraper.py       # 抓取并解析 Upcoming Matches
│       ├── coach_agents.py  # 两个 Agent（planning_agent / score_agent）与工具
│       ├── config.py        # 路径、模型、字段等配置
│       ├── storage.py       # 文件读写、成绩数据库(JSON)工具
│       ├── scores.py        # 成绩文本解析
│       └── LLMmain.py       # 旧版命令行入口（可选）
├── frontend/                # 前端（React + TypeScript + Vite）
│   └── src/
│       ├── App.tsx          # 外壳：顶部标签导航
│       ├── api.ts           # 共享 API 地址与类型
│       └── pages/
│           ├── ScoresPage.tsx  # 成绩看板：CRUD + LLM 成绩分析
│           └── ClubsPage.tsx   # 俱乐部看板：CRUD + LLM 比赛规划
├── Informations/clubs.json  # 俱乐部列表（供 CLI 使用）
├── Matches/                 # 爬取数据输出（仅限命令行自动生成，已忽略）
├── Past_Reports/            # LLM 报告归档（仅限命令行自动生成，已忽略）
├── Past_Scores/             # 结构化成绩 JSON（仅限命令行自动生成，已忽略）
├── requirements.txt         # AI 核心/CLI 依赖
└── .env                     # 环境变量（需自行创建）
```

## 环境要求

- Python 3.10+
- Node.js 18+（前端）
- 一个有效的 OpenAI API Key（仅 AI 分析/规划功能需要）

## 配置

在项目根目录创建 `.env`，写入你的 OpenAI API Key：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

## 安装与运行

需要开两个终端，分别跑后端和前端。

### 1. 后端（FastAPI）

```bash
cd backend
pip install -r requirements.txt        # 首次安装
uvicorn main:app --reload
```

- API 文档（自动生成）：http://127.0.0.1:8000/docs
- 首次启动会自动创建 SQLite 数据库 `backend/app.db` 及表。

### 2. 前端（React）

```bash
cd frontend
npm install                            # 首次安装
npm run dev
```

- 打开 http://localhost:5173 使用。

## 功能

### 成绩看板（ScoresPage）
- 新增 / 展示 / 删除成绩（对接 `/scores` 的 CRUD）。
- **LLM 成绩分析**：点「开始分析」，由 `score_agent` 根据数据库成绩生成表现评价与训练建议。

### 俱乐部看板（ClubsPage）
- 新增 / 展示 / 删除俱乐部（对接 `/clubs` 的 CRUD）。
- **LLM 比赛规划**：点「开始规划」，实时抓取各俱乐部即将进行的比赛，由 `planning_agent` 生成参赛日程规划。

## 后端 API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/scores` | 查询所有成绩 |
| POST | `/scores` | 新增成绩 |
| DELETE | `/scores/{id}` | 删除成绩 |
| POST | `/scores/import` | 一键把 `Past_Scores/scores_db.json` 导入数据库 |
| GET | `/scores/export` | 一键把数据库成绩导出为带时间戳的 JSON |
| POST | `/analyze` | 让 `score_agent` 分析数据库成绩，返回报告 |
| GET | `/clubs` | 查询所有俱乐部 |
| POST | `/clubs` | 新增俱乐部 |
| DELETE | `/clubs/{id}` | 删除俱乐部 |
| POST | `/plan` | 抓取俱乐部比赛并让 `planning_agent` 生成规划 |

## AI Agent 说明

- **`planning_agent`（比赛规划）**：接收抓取到的即将进行的比赛信息，生成时间线梳理、参赛建议、报名提醒与链接。
- **`score_agent`（成绩分析）**：生成总体评价、失分点、升级重点、阶段性训练计划、备赛重点。挂载两个工具，由模型**自行决定是否调用**：
  - `get_past_scores`：从**数据库 `scores` 表**读取历史成绩，做纵向对比、判断趋势。
  - `get_past_reports`：读取 `Past_Reports/` 下最近的历史报告，保持建议连贯。
- 当前 Agent 指令假设使用者是一名希望从 **C 级升到 B 级** 的 USPSA 射手，可在 `backend/LLMs/coach_agents.py` 中调整各 Agent 的 `instructions`。

## 命令行版本（可选，旧版）

`backend/LLMs/` 也可作为独立 CLI 运行（读取 `Informations/clubs.json`、交互式输入成绩），入口为 `LLMmain.py`：

```bash
cd backend/LLMs
python LLMmain.py
```

## 使用须知

- 本项目仅用于个人学习与研究，抓取的是网站上公开可见的比赛信息。
- 请自行遵守目标网站的服务条款（Terms of Service）与 `robots.txt`，控制请求频率，避免对站点造成压力或用于商业用途。
- 数据的时效性与准确性以网站原始页面为准，本项目不对抓取结果作任何担保。
- `app.db`、`Matches/`、`Past_Reports/`、`Past_Scores/`、`.env`、`node_modules/` 等均已在 `.gitignore` 中忽略（含个人数据与密钥，请勿手动提交）。

## 开发小记

这个项目是我学习全栈与 LLM 应用开发过程中的实践项目。由于项目开始时前端经验有限，我使用 AI 工具辅助搭建了 React + Vite 前端框架和部分初始 API 调用结构。随后我在阅读和理解代码的基础上，继续学习 React、TypeScript、组件状态和前后端交互，并自行添加和调整了一些功能。

我目前仍在继续补足前端基础，但这个项目帮助我把原本的 Python 命令行工具扩展成了一个包含 FastAPI 后端、SQLite 数据存储、OpenAI Agents SDK 工作流和 React 前端展示的全栈应用。