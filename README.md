## ItinerAI｜智能旅行规划助手（Web）

ItinerAI 是一个面向真实出行场景的**智能旅行规划 Web 应用**：通过**标准化需求采集**与**可视化景点选择**降低用户规划成本，并结合后端 **FastAPI + LangChain 多智能体**实现行程生成与“用一句话修改行程”。

> 核心定位：用“标准化采集 → 可视化选点 → 智能生成 → 一句话修改 → 导出”替代手工整理攻略。

---

## 功能亮点（MVP 可运行闭环）

- **标准化需求采集（表单）**：目的地、人数、天数、人均日预算、出行时间、节奏、偏好（多选）
- **目的地常规规划提醒**：返回“常见游玩天数/出行方式/节奏建议”，支持“一键调整”
- **景点/体验推荐与多选**：卡片展示图 + 介绍 + 花费 + 风险提示标签，支持多选确认
- **会话级本地记忆**：刷新页面可恢复进度（sessionStorage / session 级记忆）
- **多智能体协作骨架**：需求分析师 →（情报搜集/推荐）→ 行程规划师
- **行程生成（P0 最小版）**：按天拆分、基础排序与预算提示
- **一句话修改行程**：在右侧输入一句话，解析“天数 / 人均日预算”并触发重新生成
- **后端鉴权与行程 CRUD**：注册/登录、JWT 鉴权、行程数据结构化存储（含 JSONB）

---

## 技术栈

- **前端**：React + TypeScript + Vite + Ant Design + Zustand + Axios
- **后端**：Python 3.10+ + FastAPI + Pydantic + SQLAlchemy + Alembic
- **异步任务**：Celery + Redis（已完成基础配置，Windows 推荐 `solo` 池）
- **AI**：LangChain（多智能体流程骨架 + LLM/工具封装）
- **数据库**：PostgreSQL（本地开发使用 `DATABASE_URL`）

---

## 目录结构

```text
ItinerAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/        # API 路由
│   │   ├── agents/                  # 智能体（需求分析师/行程规划师等）
│   │   ├── core/                    # 配置、LLM、工具、内存等
│   │   ├── models/                  # ORM 模型
│   │   ├── schemas/                 # Pydantic 模型
│   │   ├── services/                # 业务服务（如景点推荐）
│   │   └── tasks/                   # Celery 任务
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/                     # Axios client & API 封装
    │   ├── components/              # UI 组件（含旅行图谱/表单/对话区）
    │   ├── stores/                  # Zustand 状态管理
    │   └── utils/
    └── package.json
```

---

## 快速开始（本地运行）

### 1）后端（FastAPI）

> 默认端口：`8000`

```bash
cd backend

# 建议使用 venv（如已存在可略过）
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt

# 复制环境变量
copy .env.example .env
# 然后编辑 .env，至少配置 DATABASE_URL / SECRET_KEY / OPENAI_API_KEY 等

# 启动后端
.\venv\Scripts\python -m uvicorn app.main:app --reload
```

启动后可访问 Swagger：
- `http://localhost:8000/docs`

### 2）前端（Vite）

> 默认端口：`5173`

```bash
cd frontend
npm install
npm run dev
```

前端默认通过 Axios 访问后端 API（可通过前端 `.env` 配置）：

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 可选：Redis + Celery（用于异步任务）

如果你要跑异步任务（后续“异步生成行程”等），需要 Redis 和 Celery Worker。

- 启动 Redis（示例：Docker）

```bash
docker run -d --name itinerai-redis -p 6379:6379 redis:7
```

- 启动 Celery Worker（Windows 推荐）

```bash
cd backend
celery -A celery_app worker -l info -P solo -Q itinerary,default
```

---

## 核心接口（后端）

鉴权与用户：
- `POST /api/v1/auth/register` 注册
- `POST /api/v1/auth/login` 登录（返回 `access_token`）
- `GET /api/v1/users/me` 获取当前用户

行程与闭环流程（P0）：
- `POST /api/v1/itinerary/submit-demand` 提交表单需求（写入会话记忆）
- `POST /api/v1/itinerary/get-spots` 获取推荐景点卡片（5–6 个）
- `POST /api/v1/itinerary/confirm-spots` 提交选中景点
- `POST /api/v1/itinerary/generate-itinerary` 生成行程（返回按天拆分结构）

行程 CRUD：
- `POST /api/v1/itineraries`
- `GET /api/v1/itineraries`
- `GET /api/v1/itineraries/{id}`
- `PATCH /api/v1/itineraries/{id}`

---

“标准化修改指令”解析与提示

---

## 安全与免责声明

- **请勿提交真实密钥**到仓库。后端通过 `.env` 读取密钥与配置，示例见 `backend/.env.example`。
- 本项目为求职展示用途，第三方数据源与模型调用可能受配额/网络影响。

# ItinerAI
