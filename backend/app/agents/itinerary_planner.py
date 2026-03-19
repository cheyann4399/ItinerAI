from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from app.core.memory import MemoryPayload, SessionMemory
from app.core.tools import mock_map_poi, mock_weather_forecast
from app.schemas.travel import TravelTaskBook


class ItinerarySpot(BaseModel):
  """
  单个景点在行程中的结构。
  """

  spot_name: str
  duration_hours: float = Field(..., description="预计游览时长（小时）")
  traffic: str = Field(..., description="到达方式 / 简要交通说明")
  cost: int = Field(..., description="该景点预估人均花费（元）")
  tip: List[str] = Field(
    default_factory=list,
    description="与该景点相关的提示或风险标签",
  )


class ItineraryDay(BaseModel):
  """
  每日行程结构。
  """

  day_index: int = Field(..., description="第几天，从 1 开始")
  date: str | None = Field(
    default=None,
    description="当已知具体出行日期时可填 YYYY-MM-DD，否则可为空",
  )
  weather: Dict[str, Any] = Field(
    default_factory=dict,
    description='天气信息，例如：{"condition": "sunny", "high": 26, "low": 16}',
  )
  spots: List[ItinerarySpot] = Field(
    default_factory=list,
    description="本日按顺序安排的景点列表",
  )
  total_cost: int = Field(..., description="本日预估人均总花费（元）")


class ItineraryPlan(BaseModel):
  """
  整体行程规划结果，供前端《旅行图谱》展示。
  """

  destination: str
  days: List[ItineraryDay]
  budget_hint: str = Field(
    ...,
    description="整体预算对比提示，例如：是否超出人均日预算 ±20%",
  )


def _load_travel_task_book_from_memory(memory: MemoryPayload) -> TravelTaskBook:
  if not memory.demand:
    raise ValueError("memory.demand 为空，无法生成行程")
  return TravelTaskBook.model_validate(memory.demand)


def _get_selected_spots(memory: MemoryPayload) -> List[Dict[str, Any]]:
  spots = memory.selected_spots or []
  # 简单兜底：若未选择任何景点，可以视作空行程（P1 再优化）
  return spots


def _sort_spots_by_geo(destination: str, spots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  """
  使用 mock_map_poi 简单模拟“地理排序”：优先展示与 POI 数据中名称更接近的景点。
  P0 阶段不做真实路径规划，只保证有一个确定顺序。
  """
  if not spots:
    return spots

  poi_data = mock_map_poi(destination)
  poi_spots = poi_data.get("spots", [])
  poi_names = [p.get("name", "") for p in poi_spots]

  def rank(spot: Dict[str, Any]) -> int:
    name = str(spot.get("name", ""))
    for idx, poi_name in enumerate(poi_names):
      if name and name[0] in poi_name:
        return idx
    return len(poi_names)

  return sorted(spots, key=rank)


def _build_itinerary_days(
  task_book: TravelTaskBook,
  selected_spots: List[Dict[str, Any]],
) -> List[ItineraryDay]:
  days_count = max(1, task_book.days)
  # 若未选择景点，则生成空白行程结构
  if not selected_spots:
    weather_data = mock_weather_forecast(task_book.destination, days=days_count)
    weather_days = weather_data.get("days", [])

    days: List[ItineraryDay] = []
    for i in range(days_count):
      w = weather_days[i] if i < len(weather_days) else {}
      days.append(
        ItineraryDay(
          day_index=i + 1,
          date=None,
          weather=w,
          spots=[],
          total_cost=0,
        )
      )
    return days

  # 简单规则：按排序后的景点依次平均分配到每天
  sorted_spots = _sort_spots_by_geo(task_book.destination, selected_spots)
  per_day = max(1, len(sorted_spots) // days_count) or 1

  weather_data = mock_weather_forecast(task_book.destination, days=days_count)
  weather_days = weather_data.get("days", [])

  days: List[ItineraryDay] = []
  idx = 0
  for day_idx in range(days_count):
    day_spots_raw = sorted_spots[idx : idx + per_day]
    idx += per_day
    # 最后一天接剩余所有景点
    if day_idx == days_count - 1 and idx < len(sorted_spots):
      day_spots_raw.extend(sorted_spots[idx:])

    day_spots: List[ItinerarySpot] = []
    total_cost = 0
    for s in day_spots_raw:
      cost_info = s.get("cost", {})
      ticket = int(cost_info.get("ticket", 0) or 0)
      avg_spend = int(cost_info.get("avg_spend", 0) or 0)
      spot_cost = ticket + avg_spend
      total_cost += spot_cost

      tip = s.get("risk_tags") or s.get("tip") or []

      day_spots.append(
        ItinerarySpot(
          spot_name=str(s.get("name", "")),
          duration_hours=3.0,
          traffic="就近出发，推荐公共交通 / 步行",
          cost=spot_cost,
          tip=[str(t) for t in tip],
        )
      )

    w = weather_days[day_idx] if day_idx < len(weather_days) else {}

    days.append(
      ItineraryDay(
        day_index=day_idx + 1,
        date=None,
        weather=w,
        spots=day_spots,
        total_cost=total_cost,
      )
    )

  return days


def _build_budget_hint(task_book: TravelTaskBook, days: List[ItineraryDay]) -> str:
  """
  根据 P0 要求做一个简单的预算对比提示：
  - 计算行程人均日均花费，与用户填写的 daily_budget_per_person 比较；
  - 偏差 >=20% 时给出超支 / 结余提示。
  """
  total_cost = sum(day.total_cost for day in days)
  actual_daily = total_cost / max(1, task_book.days)
  target = float(task_book.daily_budget_per_person)

  if target <= 0:
    return "尚未设置有效的人均日预算，无法进行预算对比。"

  diff_ratio = (actual_daily - target) / target
  diff_percent = round(abs(diff_ratio) * 100, 1)

  if abs(diff_ratio) < 0.2:
    return (
      f"当前行程预估人均日花费约 ¥{actual_daily:.0f}，与你的预算 ¥{target:.0f} 基本一致。"
    )

  if diff_ratio > 0:
    return (
      f"当前行程预估人均日花费约 ¥{actual_daily:.0f}，"
      f"相比你的预算 ¥{target:.0f} 超出约 {diff_percent}%。"
    )

  return (
    f"当前行程预估人均日花费约 ¥{actual_daily:.0f}，"
    f"相比你的预算 ¥{target:.0f} 略有结余（约 {diff_percent}%）。"
  )


def plan_itinerary(session_id: str) -> ItineraryPlan:
  """
  行程规划师智能体（P0 最小版）：

  1. 从 SessionMemory 读取需求（TravelTaskBook JSON）和已选景点；
  2. 通过 mock_weather_forecast / mock_map_poi 获取天气与 POI（用于排序）；
  3. 按日填充景点，并做一个简单的“地理排序”；
  4. 计算每日日总花费，并给出整体预算对比提示；
  5. 返回结构化的 ItineraryPlan，可直接用于前端《旅行图谱》展示。

  该函数不依赖前端，可在独立脚本 / 测试中直接调用。
  """
  memory = SessionMemory.get(session_id)
  task_book = _load_travel_task_book_from_memory(memory)
  selected_spots = _get_selected_spots(memory)

  days = _build_itinerary_days(task_book, selected_spots)
  budget_hint = _build_budget_hint(task_book, days)

  plan = ItineraryPlan(
    destination=task_book.destination,
    days=days,
    budget_hint=budget_hint,
  )

  # 将结果写回记忆，供后续使用
  SessionMemory.save_itinerary(session_id, plan.model_dump())

  return plan


__all__ = ["ItinerarySpot", "ItineraryDay", "ItineraryPlan", "plan_itinerary"]

