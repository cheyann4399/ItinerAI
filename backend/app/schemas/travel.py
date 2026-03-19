from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TravelTaskBook(BaseModel):
  """
  P0 核心需求结构，统一前后端 & 智能体的数据格式。

  对应 PRD 中固定选项框采集的字段：
  - 目的地
  - 人数（成人人数 / 儿童人数 / 老人数）
  - 天数
  - 人均日预算
  - 出行时间
  - 旅行节奏
  - 旅行偏好
  """

  destination: str = Field(..., description="旅行目的地城市或区域，例如：西安、青岛")

  adult_count: int = Field(..., ge=0, description="成人人数")
  child_count: int = Field(..., ge=0, description="儿童人数")
  elder_count: int = Field(..., ge=0, description="老人人数")

  days: int = Field(..., ge=1, description="游玩天数，正整数")
  daily_budget_per_person: int = Field(
    ...,
    ge=0,
    description="人均日预算（不含住宿），单位：元",
  )

  travel_time_type: Literal["weekend", "weekday", "specific_date"] = Field(
    ...,
    description="出行时间类型：周末 / 周中 / 具体日期",
  )
  travel_date: str | None = Field(
    default=None,
    description="当 travel_time_type 为 specific_date 时的具体日期（YYYY-MM-DD），否则为 None",
  )

  rhythm: Literal["fast", "slow"] = Field(
    ...,
    description="旅行节奏：fast=快节奏（3-4 个景点/天），slow=慢节奏（1-2 个景点/天）",
  )

  preferences: list[
    Literal[
      "history_culture",
      "food",
      "nature",
      "leisure",
      "creative",
      "outdoor",
    ]
  ] = Field(
    ...,
    min_length=1,
    max_length=3,
    description=(
      "旅行偏好列表，最多 3 项："
      "history_culture=历史文化, "
      "food=美食探索, "
      "nature=自然风光, "
      "leisure=休闲娱乐, "
      "creative=文化创意, "
      "outdoor=户外探险"
    ),
  )


__all__ = ["TravelTaskBook"]

