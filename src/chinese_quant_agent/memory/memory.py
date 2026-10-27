"""共享记忆：在多个 Agent 之间共享上下文与历史结果。

当前为进程内简单实现，后续可扩展为持久化存储。
"""
from __future__ import annotations

from typing import Any


class SharedMemory:
    """简单的键值共享记忆。"""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def update(self, **kwargs: Any) -> None:
        self._data.update(kwargs)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def clear(self) -> None:
        self._data.clear()
