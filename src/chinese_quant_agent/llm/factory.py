"""LLM 客户端工厂：从配置构建客户端。"""
from __future__ import annotations

from typing import Any

from .client import LLMClient


def build_client_from_settings(settings: Any) -> LLMClient:
    """从 Settings 对象构建 LLMClient，便于依赖注入。"""
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout,
    )
