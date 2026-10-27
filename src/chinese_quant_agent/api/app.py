"""FastAPI 应用：为 Vue 前端提供 REST API。

启动：cqa serve（默认 http://localhost:8000）
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings

from ..data.akshare_provider import AkshareProvider
from ..llm import build_client_from_settings
from ..orchestrator import Orchestrator
from .schemas import AnalyzeRequest, AnalyzeResponse, QuoteOut, StockItem


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    app = FastAPI(
        title="chinese-quant-agent",
        description="基于多智能体 LLM 的中文金融交易框架 API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    data = AkshareProvider()
    llm = build_client_from_settings(settings)
    orchestrator = Orchestrator(llm=llm, data=data)

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "version": "0.1.0"}

    @app.post("/api/analyze", response_model=AnalyzeResponse)
    async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
        """对单只股票执行多智能体分析。"""
        try:
            result = await orchestrator.analyze(req.symbol)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:  # noqa: BLE001
            logging.exception("分析失败")
            raise HTTPException(status_code=500, detail=f"分析失败: {e}")

        q = result["quote"]
        return AnalyzeResponse(
            symbol=result["symbol"],
            quote=QuoteOut(
                symbol=q.symbol,
                name=q.name,
                price=q.price,
                change=q.change,
                change_pct=q.change_pct,
                open=q.open,
                high=q.high,
                low=q.low,
                volume=q.volume,
                amount=q.amount,
                timestamp=q.timestamp,
            ),
            indicators=result["indicators"],
            analyses=result["analyses"],
            final_signal=result["final_signal"],
        )

    @app.get("/api/stocks/search", response_model=list[StockItem])
    async def search_stocks(q: str, limit: int = 20) -> list[StockItem]:
        """按代码/名称模糊搜索股票（用于前端联想输入）。"""
        try:
            matched = await data.search_stocks(q, limit=limit)
        except Exception as e:  # noqa: BLE001
            logging.exception("搜索股票失败")
            raise HTTPException(status_code=500, detail=f"搜索失败: {e}")
        return [StockItem(symbol=it["symbol"], name=it["name"]) for it in matched]

    @app.get("/api/stocks", response_model=list[StockItem])
    async def stocks(q: str | None = None) -> list[StockItem]:
        """获取股票列表（支持可选过滤）。"""
        try:
            df = await data.get_stock_list()
        except Exception as e:  # noqa: BLE001
            logging.exception("获取股票列表失败")
            raise HTTPException(status_code=500, detail=f"获取股票列表失败: {e}")

        items = [StockItem(symbol=str(r["代码"]), name=str(r["名称"])) for _, r in df.iterrows()]
        if q:
            qq = q.strip()
            items = [it for it in items if qq in it.symbol or qq in it.name]
        return items[:50]

    return app


app = create_app()
