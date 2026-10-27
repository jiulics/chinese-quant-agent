"""LLM 接入层：OpenAI 兼容协议，支持任意本地/云端模型。"""

from .client import LLMClient
from .factory import build_client_from_settings
from .models import LLMMessage, LLMResponse

__all__ = ["LLMClient", "LLMMessage", "LLMResponse", "build_client_from_settings"]
