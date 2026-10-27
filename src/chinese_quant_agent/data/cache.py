"""数据缓存：基于 TTL 的内存缓存，避免重复请求数据源。"""
from __future__ import annotations

import time
from typing import Any


class TTLCache:
    """简单的带 TTL 的内存缓存。"""

    def __init__(self, ttl: float = 60.0) -> None:
        self._ttl = ttl
        self._data: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._data.get(key)
        if item is None:
            return None
        ts, value = item
        if time.time() - ts > self._ttl:
            del self._data[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._data[key] = (time.time(), value)

    def clear(self) -> None:
        self._data.clear()
