"""智能助手与 AI 记忆路由。"""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ...assistant import AssistantAgent, DuckDuckGoSearch, build_search_tool
from ...data import DataProvider
from ...llm import LLMClient
from ...memory import MemoryStore
from ...tools import Registry, build_builtin_tools

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    conv_id: str = "default"


class FactRequest(BaseModel):
    content: str
    source: str = ""
    tags: list[str] | None = None


def build_router(llm: LLMClient, data: DataProvider, mock_data: DataProvider, memory: MemoryStore) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["assistant"])

    # 组装助手工具：内置 + 联网搜索
    tools = Registry()
    tools.register_many(build_builtin_tools(mock_data, memory))
    search_tool = build_search_tool(DuckDuckGoSearch())
    tools.register(search_tool)
    agent = AssistantAgent(llm, tools, memory)

    @router.post("/assistant/chat")
    async def chat(req: ChatRequest):
        result = await agent.chat(req.message, conv_id=req.conv_id)
        return result

    @router.post("/assistant/chat/stream")
    async def chat_stream(req: ChatRequest):
        async def gen():
            queue: asyncio.Queue = asyncio.Queue()

            async def cb(event: dict):
                await queue.put(event)

            async def worker():
                try:
                    result = await agent.chat(req.message, conv_id=req.conv_id, callback=cb)
                    await queue.put({"type": "done", "result": result})
                except Exception as e:  # noqa: BLE001
                    await queue.put({"type": "error", "message": str(e)})
                finally:
                    await queue.put(None)

            task = asyncio.create_task(worker())
            try:
                while True:
                    item = await queue.get()
                    if item is None:
                        break
                    yield {
                        "event": item["type"],
                        "data": json.dumps(item, ensure_ascii=False, default=str),
                    }
            finally:
                await task

        return EventSourceResponse(gen())

    @router.get("/memory/facts")
    async def list_facts(q: str | None = None, limit: int = 50):
        return await memory.list_facts(q, limit)

    @router.post("/memory/facts")
    async def add_fact(req: FactRequest):
        fid = await memory.add_fact(req.content, source=req.source, tags=req.tags)
        return {"id": fid}

    @router.delete("/memory/facts/{fid}")
    async def delete_fact(fid: str):
        ok = await memory.delete_fact(fid)
        return {"deleted": ok}

    @router.get("/memory/stats")
    async def memory_stats():
        return memory.stats()

    return router
