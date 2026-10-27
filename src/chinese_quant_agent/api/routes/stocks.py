"""股票数据路由：列表与搜索。"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..schemas import StockItem
from ...data import DataProvider

logger = logging.getLogger(__name__)


def build_router(data: DataProvider, mock_data: DataProvider) -> APIRouter:
    """构建股票数据路由。"""
    router = APIRouter(prefix="/api", tags=["stocks"])

    @router.get("/stocks/search", response_model=list[StockItem])
    async def search_stocks(q: str, limit: int = 20, use_mock: bool = False) -> list[StockItem]:
        provider = mock_data if use_mock else data
        try:
            matched = await provider.search_stocks(q, limit=limit)
        except Exception as e:  # noqa: BLE001
            logger.exception("搜索股票失败")
            raise HTTPException(status_code=500, detail=f"搜索失败: {e}")
        return [StockItem(symbol=it["symbol"], name=it["name"]) for it in matched]

    @router.get("/stocks", response_model=list[StockItem])
    async def stocks(q: str | None = None) -> list[StockItem]:
        try:
            df = await data.get_stock_list()
        except Exception:  # noqa: BLE001
            df = await mock_data.get_stock_list()
        items = [StockItem(symbol=str(r["代码"]), name=str(r["名称"])) for _, r in df.iterrows()]
        if q:
            qq = q.strip()
            items = [it for it in items if qq in it.symbol or qq in it.name]
        return items[:50]

    return router
