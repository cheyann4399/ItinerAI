from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import time

from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def log_routes_startup() -> None:
  # region agent log
  payload = {
    "sessionId": "251aeb",
    "runId": "pre-fix",
    "hypothesisId": "H1",
    "location": "app/main.py:log_routes_startup",
    "message": "FastAPI routes snapshot",
    "data": {
      "routes": [route.path for route in app.routes],
    },
    "timestamp": int(time.time() * 1000),
  }
  try:
    with open("debug-251aeb.log", "a", encoding="utf-8") as f:
      f.write(json.dumps(payload, ensure_ascii=False) + "\n")
  except Exception:
    # logging failure should not break app startup
    pass
  # endregion

# 开发环境允许的前端地址（按你的实际情况增减）
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 开发调试也可以先用 ["*"]，但上线前建议收紧
    allow_credentials=True,
    allow_methods=["*"],         # 至少包含 GET/POST/OPTIONS
    allow_headers=["*"],
)

# 所有 v1 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
  return {"status": "ok", "env": settings.app_env}


@app.get("/", summary="Root")
async def root() -> dict[str, str]:
  return {"message": "ItinerAI backend is running"}