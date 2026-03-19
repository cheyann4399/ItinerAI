from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionState(BaseModel):
  """
  会话级状态容器，用于在多智能体之间传递上下文。
  """

  current_stage: str = Field(
    default="initial_config",
    description="当前会话所处的流程阶段，例如 initial_config / demand_collecting / spot_selecting / itinerary_generating / done",
  )
  user_nickname: str | None = Field(
    default=None,
    description="用户昵称，将用于界面展示和智能体称呼",
  )
  travel_task_book: dict[str, Any] | None = Field(
    default=None,
    description="结构化的《旅行规划任务书》数据（P0：可使用 TravelTaskBook 模型对应的 JSON）",
  )
  dossier: dict[str, Any] | None = Field(
    default=None,
    description="目的地情报 dossier，后续由情报搜集类智能体写入",
  )
  itinerary: dict[str, Any] | None = Field(
    default=None,
    description="已生成的行程数据，供前端《旅行图谱》展示",
  )


class OrchestrationController:
  """
  多智能体编排的主控协调器。

  负责：
  - 持有并更新 `SessionState`
  - 根据当前阶段与用户输入，决定调用哪个智能体
  - 为后续接入 FastAPI / WebSocket 留出扩展点
  """

  def __init__(self, state: SessionState | None = None) -> None:
    self.state: SessionState = state or SessionState()

  def route_to_agent(
    self,
    user_input: str,
    *,
    metadata: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    """
    根据当前会话状态与用户输入，将请求路由到合适的智能体。

    当前仅提供方法签名与返回结构约定，具体路由实现会在后续步骤中补充。
    """
    raise NotImplementedError("Orchestration routing logic will be implemented later.")


__all__ = ["SessionState", "OrchestrationController"]

from typing import Any, Literal

from pydantic import BaseModel


class SessionState(BaseModel):
  """
  会话级状态，作为多智能体编排的上下文载体。
  """

  current_stage: Literal[
    "init",
    "requirements_collecting",
    "requirements_finalized",
    "intelligence_collecting",
    "intelligence_completed",
    "itinerary_planning",
    "itinerary_completed",
  ] = "init"
  user_nickname: str | None = None
  travel_task_book: dict[str, Any] | None = None
  dossier: dict[str, Any] | None = None
  itinerary: dict[str, Any] | None = None


class OrchestrationController:
  """
  智能体主控协调器骨架。

  负责根据当前会话状态，路由到对应的智能体（需求分析师 / 情报搜集员 / 行程规划师）。
  """

  def __init__(self, state: SessionState | None = None) -> None:
    self.state: SessionState = state or SessionState()

  def route_to_agent(self, user_input: str | None = None) -> str:
    """
    根据当前状态与用户输入，将请求路由到对应的智能体。

    当前仅提供方法骨架与基本分支，后续再接入具体智能体实现。
    """
    stage = self.state.current_stage

    if stage in {"init", "requirements_collecting"}:
      return "requirements_analyst"

    if stage in {"requirements_finalized", "intelligence_collecting"}:
      return "intelligence_collector"

    if stage in {"intelligence_completed", "itinerary_planning"}:
      return "itinerary_planner"

    return "itinerary_planner"

