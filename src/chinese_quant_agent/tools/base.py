"""工具调用抽象：定义可被 LLM function calling 调用的工具。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Tool:
    """一个工具：名字、描述、参数 schema 与执行函数。"""
    name: str
    description: str
    parameters: dict                              # JSON Schema
    func: Any                                     # 异步可调用
    meta: dict = field(default_factory=dict)

    def to_openai(self) -> dict:
        """转为 OpenAI function calling 所需的 tool 定义。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry(ABC):
    """工具注册表接口。"""

    @abstractmethod
    def list(self) -> list[Tool]:
        """返回所有可用工具。"""

    @abstractmethod
    def get(self, name: str) -> Tool | None:
        """按名字获取工具。"""
