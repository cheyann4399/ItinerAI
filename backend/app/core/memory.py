from __future__ import annotations

from threading import RLock
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryPayload(BaseModel):
  """
  会话级本地记忆载体，用于在智能体之间传递上下文。

  - demand: 用户填写的需求（对应 TravelTaskBook / 前端固定选项框 JSON）
  - selected_spots: 用户确认选择的景点 / 体验卡片列表
  - itinerary: 已生成的行程数据（供《旅行图谱》展示）
  - extra: 预留扩展字段，存放其他轻量级上下文信息
  """

  demand: Dict[str, Any] | None = Field(default=None)
  selected_spots: List[Dict[str, Any]] | None = Field(default=None)
  itinerary: Dict[str, Any] | None = Field(default=None)
  extra: Dict[str, Any] | None = Field(default=None)


class SessionMemory:
  """
  基于进程内字典的会话级本地记忆（不依赖数据库）。

  设计约束：
  - 使用 session_id 作为键（可由前端/认证系统生成并传入）
  - 单进程内多次请求共享同一份记忆，用于智能体之间的数据传递
  - 适用于 MVP / P0 场景，后续可平滑迁移到 Redis / DB
  """

  _store: Dict[str, MemoryPayload] = {}
  _lock: RLock = RLock()

  @classmethod
  def get(cls, session_id: str) -> MemoryPayload:
    """
    读取指定会话的记忆；若不存在则返回空白 MemoryPayload 并创建。
    """
    with cls._lock:
      if session_id not in cls._store:
        cls._store[session_id] = MemoryPayload()
      return cls._store[session_id]

  @classmethod
  def save_demand(cls, session_id: str, demand: Dict[str, Any]) -> MemoryPayload:
    """
    保存 / 更新用户需求（TravelTaskBook 对应的 JSON）。
    """
    with cls._lock:
      payload = cls.get(session_id)
      payload.demand = demand
      cls._store[session_id] = payload
      return payload

  @classmethod
  def save_selected_spots(
    cls,
    session_id: str,
    spots: List[Dict[str, Any]],
  ) -> MemoryPayload:
    """
    保存 / 更新用户选中的景点 / 体验列表。
    """
    with cls._lock:
      payload = cls.get(session_id)
      payload.selected_spots = spots
      cls._store[session_id] = payload
      return payload

  @classmethod
  def save_itinerary(cls, session_id: str, itinerary: Dict[str, Any]) -> MemoryPayload:
    """
    保存 / 更新行程规划结果。
    """
    with cls._lock:
      payload = cls.get(session_id)
      payload.itinerary = itinerary
      cls._store[session_id] = payload
      return payload

  @classmethod
  def update_extra(cls, session_id: str, extra: Dict[str, Any]) -> MemoryPayload:
    """
    合并更新额外上下文字段（浅合并）。
    """
    with cls._lock:
      payload = cls.get(session_id)
      base: Dict[str, Any] = payload.extra or {}
      base.update(extra)
      payload.extra = base
      cls._store[session_id] = payload
      return payload

  @classmethod
  def clear(cls, session_id: str) -> None:
    """
    清空指定会话的记忆（例如用户退出登录时）。
    """
    with cls._lock:
      cls._store.pop(session_id, None)


__all__ = ["MemoryPayload", "SessionMemory"]

