"""工具注册表与执行器。"""
from __future__ import annotations

import logging
from typing import Any

from .base import Tool

logger = logging.getLogger(__name__)


class Registry:
    """内存工具注册表。"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def register_many(self, tools: list[Tool]) -> None:
        for t in tools:
            self.register(t)

    def list(self) -> list[Tool]:
        return list(self._tools.values())

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def to_openai(self) -> list[dict]:
        return [t.to_openai() for t in self._tools.values()]

    async def execute(self, name: str, arguments: dict) -> str:
        """执行工具并返回字符串结果。"""
        tool = self._tools.get(name)
        if not tool:
            return f"未知工具: {name}"
        try:
            result = await tool.func(**arguments)
            return str(result)
        except Exception as e:  # noqa: BLE001
            logger.exception("工具执行失败: %s", name)
            return f"工具 {name} 执行失败: {e}"
