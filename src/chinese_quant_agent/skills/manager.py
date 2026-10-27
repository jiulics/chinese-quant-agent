"""Skill 中心：创建和管理自定义数据获取技能。

技能是"名称 + 描述 + 参数 schema + 可执行逻辑"的封装，
允许用户扩展数据源与获取逻辑，并供智能助手工具调用。
"""
from __future__ import annotations

import importlib
import inspect
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Skill:
    """一个可复用技能。"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        func: Any,
        source: str = "builtin",
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func
        self.source = source

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "source": self.source,
        }

    async def run(self, **kwargs) -> str:
        result = self.func(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        return str(result)


class SkillManager:
    """技能注册与管理。"""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list(self) -> list[dict]:
        return [s.to_dict() for s in self._skills.values()]

    def names(self) -> list[str]:
        return list(self._skills.keys())

    async def run(self, name: str, **kwargs) -> str:
        skill = self._skills.get(name)
        if not skill:
            return f"未知技能: {name}"
        try:
            return await skill.run(**kwargs)
        except Exception as e:  # noqa: BLE001
            logger.exception("技能执行失败: %s", name)
            return f"技能 {name} 执行失败: {e}"

    def to_tools(self) -> list:
        """将技能导出为工具列表，供智能助手调用。"""
        from ..tools.base import Tool

        async def make_runner(s: Skill):
            async def runner(**kwargs):
                return await s.run(**kwargs)
            return runner

        tools = []
        for s in self._skills.values():
            tools.append(Tool(s.name, s.description, s.parameters, None))
        # 由于 async 闭包需要绑定，这里用同步包装
        return tools
