from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.memory import SessionMemory
from app.agents.demand_analyst import DemandAnalysisResult, analyze_demand_from_form
from app.agents.itinerary_planner import ItineraryPlan, plan_itinerary
from app.models.base import get_db
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryRead
from app.schemas.travel import TravelTaskBook
from app.services.spot_recommender import (
  SpotCard,
  SpotRecommendRequest,
  SpotRecommendResponse,
  recommend_spots,
)
from app.api.v1.endpoints.itineraries import create_itinerary as _create_itinerary_core


router = APIRouter(prefix="/itinerary", tags=["itinerary"])


@router.post("/create", response_model=ItineraryRead, status_code=status.HTTP_201_CREATED)
def create_itinerary(
  payload: ItineraryCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> ItineraryRead:
  """
  兼容端点:
  POST /api/v1/itinerary/create
  内部复用 /itineraries 的创建逻辑，避免重复实现。
  """
  return _create_itinerary_core(payload=payload, db=db, current_user=current_user)


@router.post(
  "/submit-demand",
  response_model=DemandAnalysisResult,
  status_code=status.HTTP_200_OK,
)
def submit_demand(
  form: TravelTaskBook,
  current_user: User = Depends(get_current_user),
) -> DemandAnalysisResult:
  """
  提交旅行需求（固定选项框表单）。

  - 输入: TravelTaskBook (P0 核心需求结构)
  - 输出: DemandAnalysisResult (含标准化任务书 + 目的地常规建议)
  - 副作用: 将需求 JSON 写入 SessionMemory，供后续步骤使用
  """
  # 使用用户 ID 作为基础会话标识（MVP 简化处理）
  session_id = f"user-{current_user.id}"

  # 写入会话记忆
  SessionMemory.save_demand(session_id, form.model_dump())

  # 调用需求分析器生成标准化任务书 + 建议
  result = analyze_demand_from_form(form.model_dump())
  return result


@router.get(
  "/get-spots",
  response_model=SpotRecommendResponse,
  status_code=status.HTTP_200_OK,
)
def get_spots(
  current_user: User = Depends(get_current_user),
) -> SpotRecommendResponse:
  """
  根据最近一次提交的 TravelTaskBook 推荐景点卡片。

  - 输入: 会话级记忆中的 TravelTaskBook
  - 输出: SpotRecommendResponse (5-6 张卡片)
  """
  session_id = f"user-{current_user.id}"
  memory = SessionMemory.get(session_id)
  if not memory.demand:
    raise ValueError("尚未提交旅行需求，无法获取景点推荐。")

  task_book = TravelTaskBook.model_validate(memory.demand)
  req = SpotRecommendRequest(
    destination=task_book.destination,
    preferences=list(task_book.preferences),
  )
  res = recommend_spots(req)
  return res


@router.post(
  "/confirm-spots",
  response_model=dict,
  status_code=status.HTTP_200_OK,
)
def confirm_spots(
  spots: list[SpotCard],
  current_user: User = Depends(get_current_user),
) -> dict:
  """
  确认用户选择的景点卡片。

  - 输入: SpotCard 列表（前端多选结果）
  - 输出: 简单确认结果
  - 副作用: 将选中景点写入 SessionMemory
  """
  session_id = f"user-{current_user.id}"
  serialized = [s.model_dump() for s in spots]
  SessionMemory.save_selected_spots(session_id, serialized)
  return {"status": "ok", "selected_count": len(serialized)}


@router.post(
  "/generate-itinerary",
  response_model=ItineraryPlan,
  status_code=status.HTTP_200_OK,
)
def generate_itinerary(
  current_user: User = Depends(get_current_user),
) -> ItineraryPlan:
  """
  生成行程：

  - 从 SessionMemory 中读取 TravelTaskBook + 已选景点；
  - 调用行程规划师 plan_itinerary；
  - 返回结构化 ItineraryPlan。
  """
  session_id = f"user-{current_user.id}"
  plan = plan_itinerary(session_id)
  return plan


class ModifyItineraryRequest(BaseModel):
  """
  ⽣成后修改需求的请求体（最⼩化版本，仅⽀持天数和预算）。
  """

  days: int | None = Field(
    default=None,
    ge=1,
    description="新的游玩天数（正整数），为空表示不修改该字段",
  )
  daily_budget_per_person: int | None = Field(
    default=None,
    ge=0,
    description="新的⼈均⽇预算（元，不含住宿），为空表示不修改该字段",
  )


@router.post(
  "/modify-and-regenerate",
  response_model=ItineraryPlan,
  status_code=status.HTTP_200_OK,
)
def modify_and_regenerate_itinerary(
  payload: ModifyItineraryRequest,
  current_user: User = Depends(get_current_user),
) -> ItineraryPlan:
  """
  ⾏程⽣成后，通过标准化参数修改需求并重新⽣成⾏程。

  - 修改会话记忆中的 TravelTaskBook（天数 / 预算等）
  - 清理旧⾏程（由 plan_itinerary 内部重写）
  - 返回新的 ItineraryPlan
  """
  session_id = f"user-{current_user.id}"
  memory = SessionMemory.get(session_id)
  if not memory.demand:
    raise ValueError("尚未提交旅行需求，无法修改⾏程。")

  task_book = TravelTaskBook.model_validate(memory.demand)

  if payload.days is not None:
    task_book.days = payload.days
  if payload.daily_budget_per_person is not None:
    task_book.daily_budget_per_person = payload.daily_budget_per_person

  # 写回需求记忆
  SessionMemory.save_demand(session_id, task_book.model_dump())

  # 重新⽣成⾏程（内部会覆盖记忆中的 itinerary）
  plan = plan_itinerary(session_id)
  return plan


