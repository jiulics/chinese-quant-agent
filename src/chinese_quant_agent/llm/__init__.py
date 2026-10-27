"""LLM 接入层：OpenAI 兼容协议，支持任意本地/云端模型。"""

from .client import LLMClient, LLMMessage, LLMResponse, build_client_from_settings

__all__ = ["LLMClient", "LLMMessage", "LLMResponse", "build_client_from_settings"]
