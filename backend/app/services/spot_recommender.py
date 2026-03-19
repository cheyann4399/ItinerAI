from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from app.core.tools import mock_map_poi, mock_spot_search


class SpotCard(BaseModel):
  """
  前端景点卡片显示所需的最小结构。
  """

  id: str
  name: str
  thumbnail: str = Field(..., description="缩略图 URL（可为占位图）")
  description: str = Field(
    ...,
    description="简要介绍：是什么 / 适合人群 / 可做的事（3 点归纳）",
  )
  crowd: str = Field(..., description="适合人群标签，例如：家庭 / 年轻人 / 老少皆宜")
  cost: Dict[str, Any] = Field(
    ...,
    description='费用信息，例如：{"ticket": 80, "avg_spend": 150}，无票价时 ticket=0 或 "free"',
  )
  risk_tags: List[str] = Field(
    default_factory=list,
    description='风险提示标签列表，例如：["需预约", "节假日限流", "周一闭园"]',
  )
  poi_location: Dict[str, Any] = Field(
    default_factory=dict,
    description='地理位置相关信息，例如：{"lat": 34.26, "lng": 108.95, "address": "..."}',
  )


class SpotRecommendRequest(BaseModel):
  """
  景点推荐输入需求：目的地 + 偏好。
  """

  destination: str
  preferences: List[str] = Field(
    default_factory=list,
    description="旅行偏好标签列表（history_culture / food / nature / leisure / creative / outdoor）",
  )


class SpotRecommendResponse(BaseModel):
  """
  景点推荐输出结果：5-6 个卡片式景点。
  """

  destination: str
  spots: List[SpotCard]


def _build_spot_cards_from_mock(
  destination: str,
  preferences: List[str],
) -> List[SpotCard]:
  """
  基于 mock_spot_search + mock_map_poi 构造卡片列表。
  """
  # 调用景点搜索模拟工具，获取基础景点信息
  raw = mock_spot_search(destination, preferences)
  raw_spots: List[Dict[str, Any]] = raw.get("spots", [])

  # 调用 POI 模拟工具，用于补充地理位置（这里只使用前两个点做示例）
  poi_data = mock_map_poi(destination)
  poi_spots = poi_data.get("spots", [])

  poi_by_index: Dict[int, Dict[str, Any]] = {
    idx: poi for idx, poi in enumerate(poi_spots)
  }

  cards: List[SpotCard] = []
  for idx, spot in enumerate(raw_spots):
    poi_location = poi_by_index.get(idx, {})

    # 从 mock_spot_search 的 tip 字段中直接作为风险标签
    risk_tags = spot.get("tip", [])

    card = SpotCard(
      id=str(spot.get("id", f"spot_{idx+1}")),
      name=str(spot.get("name", f"{destination}景点 {idx+1}")),
      thumbnail=str(spot.get("img", "https://example.com/mock.jpg")),
      description=str(spot.get("desc", "")),
      crowd=str(spot.get("crowd", "老少皆宜")),
      cost=spot.get("cost", {"ticket": 0, "avg_spend": 0}),
      risk_tags=[str(tag) for tag in risk_tags],
      poi_location={
        "lat": poi_location.get("lat"),
        "lng": poi_location.get("lng"),
        "address": poi_location.get("address"),
      },
    )
    cards.append(card)

  # 只保留前 6 个，保证 5-6 个卡片输出
  return cards[:6]


def recommend_spots(
  request: SpotRecommendRequest,
) -> SpotRecommendResponse:
  """
  P0 景点推荐核心入口。

  - 输入：目的地 + 偏好
  - 输出：5-6 个包含图片 / 介绍 / 风险提示的景点卡片

  设计为纯函数，可独立运行测试，不依赖其他智能体。
  """
  cards = _build_spot_cards_from_mock(
    destination=request.destination,
    preferences=request.preferences,
  )

  # 若为小众地点（mock 视作 raw_spots 为空），自动补充简单示例景点
  if not cards:
    fallback_cards: List[SpotCard] = []
    for idx, name in enumerate(["本地书店", "人气商场", "文化展览"], start=1):
      fallback_cards.append(
        SpotCard(
          id=f"fallback_{idx}",
          name=f"{request.destination}{name}",
          thumbnail="https://example.com/mock-fallback.jpg",
          description=f"{request.destination}{name}，用于小众目的地的兜底展示示例。",
          crowd="老少皆宜",
          cost={"ticket": 0, "avg_spend": 100},
          risk_tags=[],
          poi_location={},
        )
      )
    cards = fallback_cards

  # 确保不超过 6 个；mock_spot_search 默认已返回 5 个
  cards = cards[:6]

  return SpotRecommendResponse(
    destination=request.destination,
    spots=cards,
  )


__all__ = ["SpotCard", "SpotRecommendRequest", "SpotRecommendResponse", "recommend_spots"]

