# USPSA Match Planner with LLM

一个已部署到 Azure 的全栈 USPSA 比赛助手。项目使用 React 管理成绩与俱乐部数据，使用 FastAPI 提供 REST API，并通过 OpenAI Agents SDK 生成成绩分析和比赛规划。

> 当前版本是单用户演示系统：所有访问者共享同一组成绩、俱乐部和分析报告。项目尚未实现登录、用户身份验证或按用户隔离的数据所有权，不应存放敏感信息。

## 在线演示

- 前端：[Azure Static Web Apps](https://gray-island-02033db0f.7.azurestaticapps.net/)
- 后端健康检查：[Azure Container Apps](https://uspsa-api.delightfulbeach-9485b16e.eastus.azurecontainerapps.io/)
- API 文档：[FastAPI Swagger UI](https://uspsa-api.delightfulbeach-9485b16e.eastus.azurecontainerapps.io/docs)

## 当前云端架构

```text
Browser
   |
   v
React + Vite
Azure Static Web Apps
   |
   | HTTPS REST requests
   v
FastAPI + Uvicorn
Azure Container Apps
   |
   | SQLAlchemy / psycopg / TLS
   v
Azure Database for PostgreSQL

GitHub Actions
   |
   v
Docker build -> Azure Container Registry -> Container Apps revision
```

生产部署使用以下 Azure 服务：

| 层 | 服务 | 作用 |
|---|---|---|
| 前端 | Azure Static Web Apps | 构建并托管 React/Vite 静态站点 |
| 后端 | Azure Container Apps | 运行 Docker 化的 FastAPI 服务并提供 HTTPS |
| 镜像 | Azure Container Registry | 保存 GitHub Actions 构建的后端镜像 |
| 数据库 | Azure Database for PostgreSQL Flexible Server | 持久化成绩、俱乐部和 LLM 报告 |
| 日志 | Log Analytics Workspace | 收集 Container Apps 日志 |
| CI | GitHub Actions | 构建前端、构建并推送后端镜像 |

## 主要功能

### 成绩看板

- 新增、查看和删除 USPSA combined match 成绩。
- 记录百分比、得分、时间、组别、级别、Power Factor 和命中分布。
- 使用 LLM 分析历史表现、主要失分点和训练重点。
- 将成功生成的分析报告写入 PostgreSQL，供后续 Agent 保持建议连贯。

### 俱乐部与比赛规划

- 新增、查看和删除俱乐部。
- 抓取公开可见的 PractiScore 比赛信息。
- 使用当前级别、历史成绩和即将进行的比赛生成规划建议。

### LLM 数据工具

Agent 工具与 FastAPI 共享同一个 SQLAlchemy `SessionLocal`：

- `get_past_scores`：从当前 `DATABASE_URL` 指向的数据库读取历史成绩。
- `get_class`：从最新一条成绩读取当前 USPSA 级别。
- `get_past_reports`：从 PostgreSQL 的 `analysis_reports` 表读取最近三份分析报告。

本地未设置 `DATABASE_URL` 时默认使用 SQLite；Azure 通过 Container Apps Secret 注入 PostgreSQL 连接字符串。

## 技术栈

| 类别 | 技术 |
|---|---|
| 前端 | React 19、TypeScript、Vite |
| 后端 | FastAPI、Uvicorn、Pydantic |
| 数据访问 | SQLAlchemy、psycopg |
| 本地数据库 | SQLite |
| 云数据库 | Azure Database for PostgreSQL |
| AI | OpenAI Agents SDK、OpenAI API |
| 抓取 | cloudscraper、BeautifulSoup |
| 容器 | Docker |
| CI/CD | GitHub Actions、Azure Static Web Apps、Azure Container Apps |

## 目录结构

```text
.
├── .github/workflows/
│   ├── azure-container-apps.yml
│   └── azure-static-web-apps-gray-island-02033db0f.yml
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── analysis.py
│   ├── import_export.py
│   ├── requirements.txt
│   └── LLMs/
│       ├── coach_agents.py
│       ├── config.py
│       ├── scraper.py
│       ├── storage.py
│       └── LLMmain.py
├── frontend/
│   ├── src/
│   │   ├── api.ts
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── Informations/
├── Matches/
├── Past_Reports/
└── Past_Scores/
```

## 数据模型

云端数据库当前包含：

| 表 | 说明 |
|---|---|
| `scores` | USPSA 比赛成绩 |
| `clubs` | 俱乐部名称和 URL |
| `analysis_reports` | LLM 生成的历史成绩分析 |

`Base.metadata.create_all()` 会在应用启动时创建缺少的表。该方式适合当前增量开发；后续涉及列变更和正式迁移时，计划引入 Alembic。

## 环境变量

### 后端

| 变量 | 必需 | 说明 |
|---|---|---|
| `OPENAI_API_KEY` | 使用 AI 功能时必需 | OpenAI API Key |
| `DATABASE_URL` | 否 | SQLAlchemy 连接字符串；未设置时使用 `sqlite:///./app.db` |
| `ALLOWED_ORIGINS` | 否 | 逗号分隔的 CORS来源列表 |
| `PORT` | 否 | 容器监听端口，默认 `8000` |

Azure 中的 `OPENAI_API_KEY` 和 `DATABASE_URL` 通过 Container Apps Secret引用，不应提交到 Git。

PostgreSQL连接字符串示例：

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/uspsa?sslmode=require
```

### 前端

| 变量 | 必需 | 说明 |
|---|---|---|
| `VITE_API_URL` | 否 | 后端根地址；本地默认 `http://127.0.0.1:8000` |

不要把 `OPENAI_API_KEY` 放进 `VITE_*` 变量。Vite 会把这些值写入浏览器可下载的前端资源。

## 本地运行

### 1. 启动后端

```bash
cd backend
python -m venv .venv

# PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

本地地址：

- API：<http://127.0.0.1:8000>
- Swagger UI：<http://127.0.0.1:8000/docs>

如果不设置 `DATABASE_URL`，首次启动会在 `backend/app.db` 创建 SQLite 表。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：<http://localhost:5173>

如需连接其他后端：

```powershell
$env:VITE_API_URL = "https://your-api.example.com"
npm run dev
```

## Docker

在仓库根目录构建后端镜像：

```bash
docker build -t uspsa-api:local ./backend
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e DATABASE_URL=sqlite:///./app.db \
  uspsa-api:local
```

生产部署不会把 `.env` 或数据库密码复制进镜像。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/` | 健康检查 |
| `GET` | `/scores` | 查询全部成绩 |
| `POST` | `/scores` | 新增成绩 |
| `DELETE` | `/scores/{id}` | 删除成绩 |
| `POST` | `/scores/import` | 从本地 JSON 导入成绩 |
| `GET` | `/scores/export` | 将成绩导出为 JSON |
| `POST` | `/analyze` | 生成并持久化 LLM 成绩分析 |
| `GET` | `/clubs` | 查询全部俱乐部 |
| `POST` | `/clubs` | 新增俱乐部 |
| `DELETE` | `/clubs/{id}` | 删除俱乐部 |
| `POST` | `/plan` | 抓取比赛并生成 LLM 规划 |

## CI/CD

### 前端

推送到 `main` 后，Static Web Apps workflow 会：

1. 安装前端依赖。
2. 使用 `VITE_API_URL` 构建 React。
3. 自动发布到 Azure Static Web Apps。

### 后端

修改 `backend/**` 并推送到 `main` 后，Container workflow 会：

1. 使用 `backend/Dockerfile` 构建镜像。
2. 使用 GitHub Secrets 登录 ACR。
3. 将 `uspsa-api:latest` 推送到 Azure Container Registry。

当前学生订阅无法创建 GitHub所需的 Entra服务主体，因此 workflow 暂时不会自动更新 Container App。镜像构建成功后，需要手动创建新 revision：

```powershell
$revisionSuffix = "release-" + (Get-Date -Format "yyyyMMddHHmmss")

az containerapp update `
  --name uspsa-api `
  --resource-group rg-uspsa-demo `
  --image cacbba25a6beacr.azurecr.io/uspsa-api:latest `
  --revision-suffix $revisionSuffix
```

## 验证

后端基础检查：

```bash
python -m compileall backend
```

前端检查：

```bash
cd frontend
npm run lint
npm run build
```

部署后可查看日志：

```powershell
az containerapp logs show `
  --name uspsa-api `
  --resource-group rg-uspsa-demo `
  --follow
```

## 当前限制与安全边界

- 当前没有登录系统，所有访问者共享同一数据库内容。
- `scores`、`clubs` 和 `analysis_reports` 尚未包含 `user_id`。
- CORS 不是身份验证；知道 API地址的访问者仍可能直接调用公开接口。
- 不应在当前公开部署中保存敏感或私密数据。
- Container Apps中的 `Matches/`、`Past_Reports/` 和导出文件仍属于临时文件；正式持久化数据应保存在 PostgreSQL。
- 外部比赛信息的准确性和时效性以来源页面为准，应遵守目标网站服务条款并控制请求频率。

计划中的多用户方案是后端签发匿名 Token、数据库按 `owner_id` 隔离数据，并允许匿名身份以后升级为正式账号。IP地址只用于限流和反滥用，不作为用户身份。

## 项目定位

本项目用于学习和展示：

- Python全栈开发与前后端 API设计；
- React组件化和可复用 CRUD界面；
- SQLAlchemy从本地 SQLite到云端 PostgreSQL的迁移；
- Docker镜像、ACR和 Azure Container Apps部署；
- Static Web Apps与 GitHub Actions；
- LLM Agent工具调用、历史上下文和结果持久化。

项目开发过程中使用了 AI工具辅助搭建、重构和排查部署问题。代码、配置和部署结果由项目作者阅读、执行并验证。
