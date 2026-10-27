"""SSE 流式分析端点：实时推送多智能体分析过程。

将流式事件序列化逻辑从 app.py 中抽离，保持路由文件精简。
"""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from ..orchestrator import Orchestrator
from .schemas import AnalyzeRequest

logger = logging.getLogger(__name__)


def _serialize_done(result: dict) -> dict:
    """将分析结果精简为可 JSON 序列化的 done 事件载荷。"""
    q = result["quote"]
    return {
        "type": "done",
        "symbol": result["symbol"],
        "final_signal": result["final_signal"],
        "depth": result["depth"],
        "scenarios": result.get("scenarios"),
        "quote": {
            "name": q.name,
            "price": q.price,
            "change_pct": q.change_pct,
        },
        "indicators": result["indicators"],
        "analyses": result.get("analyses_structured", []),
    }


async def stream_analysis(orch: Orchestrator, req: AnalyzeRequest):
    """返回 SSE EventSourceResponse，流式推送分析过程。"""
    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()

        async def callback(event: dict):
            await queue.put(event)

        async def worker():
            try:
                result = await orch.analyze(req.symbol, depth=req.depth, callback=callback)
                await queue.put(_serialize_done(result))
            except Exception as e:  # noqa: BLE001
                logger.exception("流式分析失败")
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

    return EventSourceResponse(event_generator())
