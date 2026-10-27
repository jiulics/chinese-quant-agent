"""分析相关路由：/analyze 与 /analyze/stream。"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..schemas import AnalyzeRequest, AnalyzeResponse, QuoteOut
from ...data import DataProvider
from ...llm import LLMClient
from ...orchestrator import Orchestrator
from ..stream import stream_analysis

logger = logging.getLogger(__name__)


def _quote_to_out(q) -> QuoteOut:
    return QuoteOut(
        symbol=q.symbol, name=q.name, price=q.price, change=q.change,
        change_pct=q.change_pct, open=q.open, high=q.high, low=q.low,
        volume=q.volume, amount=q.amount, timestamp=q.timestamp,
    )


def build_router(
    llm: LLMClient,
    data: DataProvider,
    mock_data: DataProvider,
) -> APIRouter:
    """构建分析路由（依赖注入，运行时按 use_mock 切换数据源）。"""
    router = APIRouter(prefix="/api", tags=["analyze"])

    def _pick_orch(use_mock: bool) -> Orchestrator:
        return Orchestrator(llm=llm, data=mock_data if use_mock else data)

    @router.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
        orch = _pick_orch(req.use_mock)
        try:
            result = await orch.analyze(req.symbol, depth=req.depth)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:  # noqa: BLE001
            logger.exception("分析失败")
            raise HTTPException(status_code=500, detail=f"分析失败: {e}")

        return AnalyzeResponse(
            symbol=result["symbol"],
            quote=_quote_to_out(result["quote"]),
            indicators=result["indicators"],
            analyses=result["analyses"],
            scenarios=result.get("scenarios"),
            final_signal=result["final_signal"],
            depth=result["depth"],
        )

    @router.post("/analyze/stream")
    async def analyze_stream(req: AnalyzeRequest):
        orch = _pick_orch(req.use_mock)
        return await stream_analysis(orch, req)

    return router
