from typing import Any, Dict, List
from datetime import date, timedelta

from langchain_community.tools import DuckDuckGoSearchRun


def get_search_tool() -> DuckDuckGoSearchRun:
  """
  返回单个 DuckDuckGo 搜索工具实例，用于简单搜索场景。
  """
  return DuckDuckGoSearchRun()


def mock_map_poi(destination: str, category: str = "scenic") -> Dict[str, Any]:
  """
  地图 / POI 模拟工具（最小化可用版）。

  返回指定目的地 + 分类下的一组示例 POI，结构固定，便于智能体解析。
  """
  base_spots = [
    {
      "id": "poi_1",
      "name": f"{destination}核心景点 A",
      "lat": 34.26,
      "lng": 108.95,
      "address": f"{destination}示例地址 1 号",
    },
    {
      "id": "poi_2",
      "name": f"{destination}核心景点 B",
      "lat": 34.27,
      "lng": 108.97,
      "address": f"{destination}示例地址 2 号",
    },
  ]

  return {
    "destination": destination,
    "category": category,
    "spots": base_spots,
  }


def mock_weather_forecast(destination: str, days: int = 3) -> Dict[str, Any]:
  """
  天气预报模拟工具（最小化可用版）。

  返回未来 N 天的简易天气信息。
  """
  today = date.today()
  forecasts: List[Dict[str, Any]] = []

  for i in range(max(1, days)):
    d = today + timedelta(days=i)
    forecasts.append(
      {
        "date": d.isoformat(),
        "condition": "sunny" if i % 2 == 0 else "cloudy",
        "high": 26 - i,
        "low": 16 - i,
      }
    )

  return {"destination": destination, "days": forecasts}


def mock_spot_search(destination: str, preferences: List[str]) -> Dict[str, Any]:
  """
  景点 / 特色情报模拟工具（最小化可用版）。

  返回与旅行偏好大致匹配的 5-6 个“卡片式”景点结构。
  """
  tags = preferences or ["history_culture"]

  spots: List[Dict[str, Any]] = []
  for idx in range(1, 6):
    spots.append(
      {
        "id": f"spot_{idx}",
        "name": f"{destination}示例景点 {idx}",
        "desc": f"与偏好 {', '.join(tags)} 相关的示例景点 {idx}，用于行程规划演示。",
        "crowd": "老少皆宜",
        "do": ["拍照打卡", "轻松漫步"],
        "cost": {
          "ticket": 0 if idx % 2 == 0 else 80,
          "avg_spend": 100 + idx * 20,
        },
        "tip": ["需预约"] if idx % 3 == 0 else ["节假日人多，建议错峰"],
        "img": "https://example.com/mock.jpg",
      }
    )

  return {"destination": destination, "preferences": tags, "spots": spots}


def get_default_tools() -> List[Any]:
  """
  返回一组默认可用工具，后续在智能体/Agent 配置中直接复用。

  当前包括：
  - DuckDuckGo 通用搜索
  - mock_map_poi: 地图 / POI 模拟
  - mock_weather_forecast: 天气模拟
  - mock_spot_search: 景点 / 特色情报模拟
  """
  return [
    get_search_tool(),
    mock_map_poi,
    mock_weather_forecast,
    mock_spot_search,
  ]


search_tool = get_search_tool()
default_tools = get_default_tools()

