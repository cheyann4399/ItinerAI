from __future__ import annotations

from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

from app.schemas.travel import TravelTaskBook


class DestinationSuggestion(BaseModel):
  """
  目的地常规规划建议，用于“目的地常规提醒 + 一键调整”。
  """

  recommended_days: int = Field(..., description="该目的地多数游客推荐游玩天数")
  main_transport: Literal["self_drive", "public_transport"] = Field(
    ...,
    description="主要出行方式：自驾 / 公共交通",
  )
  fast_spots_per_day: int = Field(
    ...,
    description="快节奏时建议的每日景点数量",
  )
  slow_spots_per_day: int = Field(
    ...,
    description="慢节奏时建议的每日景点数量",
  )
  adjust_message: str = Field(
    ...,
    description="给用户的一句话调整建议文案",
  )


class DemandAnalysisResult(BaseModel):
  """
  需求分析师输出结果：
  - 标准化 TravelTaskBook（P0 核心数据结构）
  - 目的地常规规划建议（用于“一键调整”）
  """

  travel_task_book: TravelTaskBook
  destination_suggestion: DestinationSuggestion


def _mock_destination_suggestion(
  destination: str,
  user_days: int,
  rhythm: str,
) -> DestinationSuggestion:
  """
  最小化可用版：不依赖外部 API，基于简单规则生成目的地常规建议。

  后续可以替换为真实地图 / 行业数据接口。
  """
  big_cities = {"北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安"}
  main_transport: Literal["self_drive", "public_transport"] = (
    "public_transport" if destination in big_cities else "self_drive"
  )

  # 简单规则：大城市推荐 4 天，小城市推荐 3 天
  recommended_days = 4 if destination in big_cities else 3

  fast_spots_per_day = 4
  slow_spots_per_day = 2

  if user_days < recommended_days:
    adjust_message = (
      f"建议将行程天数从 {user_days} 天调整为 {recommended_days} 天，"
      f"目前为 {rhythm} 节奏，推荐每天安排 "
      f"{fast_spots_per_day if rhythm == 'fast' else slow_spots_per_day} 个景点。"
    )
  elif user_days > recommended_days:
    adjust_message = (
      f"该目的地多数游客通常游玩 {recommended_days} 天，你当前设置为 {user_days} 天，"
      "如需更轻松的行程可以考虑缩短天数。"
    )
  else:
    adjust_message = (
      f"你的行程天数（{user_days} 天）与该目的地常规游玩天数一致，"
      "可直接进入下一步景点选择。"
    )

  return DestinationSuggestion(
    recommended_days=recommended_days,
    main_transport=main_transport,
    fast_spots_per_day=fast_spots_per_day,
    slow_spots_per_day=slow_spots_per_day,
    adjust_message=adjust_message,
  )


def analyze_demand_from_form(form_data: Dict[str, Any]) -> DemandAnalysisResult:
  """
  需求分析师智能体（表单版）：

  1. 接收前端固定表单 JSON（与 TravelTaskBook 字段一致）；
  2. 构建标准化 TravelTaskBook；
  3. 生成目的地常规规划建议（用于“一键调整”）。

  不进行任何对话采集，也不依赖其他智能体。
  """
  task_book = TravelTaskBook(**form_data)

  suggestion = _mock_destination_suggestion(
    destination=task_book.destination,
    user_days=task_book.days,
    rhythm=task_book.rhythm,
  )

  return DemandAnalysisResult(
    travel_task_book=task_book,
    destination_suggestion=suggestion,
  )


__all__ = ["DestinationSuggestion", "DemandAnalysisResult", "analyze_demand_from_form"]

