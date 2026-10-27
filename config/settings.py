"""全局配置：基于 pydantic-settings，从环境变量 / .env 读取。

每个开发者都可以通过 .env 自定义自己的 LLM 模型（纯本地运行无需联网）。
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置。字段名对应环境变量（大小写不敏感）。"""

    # ---------- LLM ----------
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096
    llm_timeout: float = 120.0

    # ---------- 数据源 ----------
    data_provider: Literal["akshare"] = "akshare"

    # ---------- 调试 ----------
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。"""
    return Settings()
