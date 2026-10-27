"""持久化记忆存储：项目级记忆 + 事实沉淀。

使用 JSON 文件持久化，支持：
- 事实（facts）：从研究过程中抽取并固化的关键事实
- 会话记忆（sessions）：跨会话的项目上下文
- 对话历史（conversations）：智能助手的历史

线程安全：通过 asyncio.Lock 串行化写操作。
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryStore:
    """基于 JSON 文件的持久化记忆存储。"""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path else Path(".cqa_memory.json")
        self._lock = asyncio.Lock()
        self._data: dict[str, Any] = {
            "facts": {},          # fact_id -> {content, source, tags, created_at}
            "sessions": {},        # session_id -> {context, updated_at}
            "conversations": {},   # conv_id -> [ {role, content} ... ]
        }
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                logger.warning("记忆文件读取失败，使用空记忆: %s", e)
                self._data = {"facts": {}, "sessions": {}, "conversations": {}}

    async def _save(self) -> None:
        async with self._lock:
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._path)

    # ---------- 事实沉淀 ----------
    async def add_fact(self, content: str, *, source: str = "", tags: list[str] | None = None) -> str:
        """新增一条事实，返回 fact_id。"""
        import uuid
        fid = uuid.uuid4().hex[:12]
        self._data["facts"][fid] = {
            "content": content,
            "source": source,
            "tags": tags or [],
            "created_at": time.time(),
        }
        await self._save()
        return fid

    async def list_facts(self, query: str | None = None, limit: int = 50) -> list[dict]:
        """列出事实，可按关键词过滤。"""
        facts = []
        for fid, f in self._data["facts"].items():
            item = {"id": fid, **f}
            if query and query not in f["content"]:
                continue
            facts.append(item)
        facts.sort(key=lambda x: x["created_at"], reverse=True)
        return facts[:limit]

    async def delete_fact(self, fid: str) -> bool:
        if fid in self._data["facts"]:
            del self._data["facts"][fid]
            await self._save()
            return True
        return False

    # ---------- 会话记忆 ----------
    async def set_session(self, session_id: str, context: dict) -> None:
        self._data["sessions"][session_id] = {"context": context, "updated_at": time.time()}
        await self._save()

    async def get_session(self, session_id: str) -> dict | None:
        s = self._data["sessions"].get(session_id)
        return s["context"] if s else None

    # ---------- 对话历史 ----------
    async def append_message(self, conv_id: str, role: str, content: str) -> None:
        self._data["conversations"].setdefault(conv_id, []).append({
            "role": role, "content": content, "ts": time.time(),
        })
        # 限制长度，避免无限增长
        self._data["conversations"][conv_id] = self._data["conversations"][conv_id][-200:]
        await self._save()

    async def get_conversation(self, conv_id: str, limit: int = 50) -> list[dict]:
        msgs = self._data["conversations"].get(conv_id, [])
        return [{"role": m["role"], "content": m["content"]} for m in msgs[-limit:]]

    # ---------- 统计 ----------
    def stats(self) -> dict:
        return {
            "facts": len(self._data["facts"]),
            "sessions": len(self._data["sessions"]),
            "conversations": len(self._data["conversations"]),
        }
