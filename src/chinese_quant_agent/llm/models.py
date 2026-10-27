"""LLM 数据模型：消息与响应。"""
from __future__ import annotations

from typing import Any


class LLMMessage:
    """一条对话消息。"""

    __slots__ = ("role", "content")

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMResponse:
    """模型返回结果。"""

    __slots__ = ("content", "raw")

    def __init__(self, content: str, raw: Any = None) -> None:
        self.content = content
        self.raw = raw
