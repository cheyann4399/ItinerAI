from functools import lru_cache
from typing import Optional

from langchain_community.chat_models import ChatOpenAI

from .config import get_settings


class LLMSettings:
  """
  轻量封装，专门用于 LLM 相关配置，避免污染全局 Settings。
  """

  def __init__(
    self,
    api_key: str,
    base_url: Optional[str] = None,
    model: str = "moonshot-v1-128k",
  ) -> None:
    self.api_key = api_key
    self.base_url = base_url
    self.model = model


@lru_cache(maxsize=1)
def get_llm_settings() -> LLMSettings:
  """
  加载 Kimi / OpenAI 兼容接口配置。

  优先顺序：
  1. backend/.env 中通过 Settings 解析的字段：
     - kimi_api_key / kimi_base_url / kimi_model
  2. 进程环境变量：
     - KIMI_API_KEY / KIMI_BASE_URL / KIMI_MODEL
     - 兼容 OPENAI_API_KEY / OPENAI_BASE_URL
  """
  settings = get_settings()

  import os

  api_key = (
    (settings.kimi_api_key or "").strip()
    or os.getenv("KIMI_API_KEY")
    or os.getenv("OPENAI_API_KEY", "")
  )
  base_url = (
    (settings.kimi_base_url or None)
    or os.getenv("KIMI_BASE_URL")
    or os.getenv("OPENAI_BASE_URL")
  )
  model = (settings.kimi_model or "").strip() or os.getenv("KIMI_MODEL") or "moonshot-v1-128k"

  if not api_key:
    raise RuntimeError(
      "KIMI_API_KEY 未配置，请在 backend/.env 或环境变量中设置 KIMI_API_KEY。"
    )

  return LLMSettings(api_key=api_key, base_url=base_url, model=model)


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
  """
  返回一个全局复用的 ChatOpenAI 实例，指向 Kimi/OpenAI 兼容接口。
  """
  llm_settings = get_llm_settings()

  return ChatOpenAI(
    api_key=llm_settings.api_key,
    base_url=llm_settings.base_url,
    model=llm_settings.model,
    temperature=0.2,
  )


# 为了便于快速导入，提供一个模块级别的默认实例
llm = get_llm()

