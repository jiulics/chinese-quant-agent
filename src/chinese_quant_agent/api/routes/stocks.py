"""股票数据路由：列表与搜索。"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

import math

import pandas as pd

from ..schemas import StockItem
from ...data import DataProvider, TencentProvider

logger = logging.getLogger(__name__)


def build_router(data: DataProvider, mock_data: DataProvider, tencent: TencentProvider | None = None) -> APIRouter:
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

    @router.get("/market/indices")
    async def market_indices():
        """返回主要大盘指数快照（优先盘中实时，回退日频）。"""
        # 1. 优先腾讯盘中实时
        if tencent is not None:
            try:
                live = await tencent.get_realtime_indices()
                if live:
                    return live
            except Exception as e:  # noqa: BLE001
                logger.warning("腾讯实时指数获取失败，回退 BaoStock: %s", e)
        # 2. 回退 BaoStock 日频
        try:
            return await data.get_indices()
        except Exception:  # noqa: BLE001
            return []

    @router.get("/stocks/{symbol}/kline")
    async def stock_kline(symbol: str, days: int = 250, period: str = "daily"):
        """返回个股历史 K 线（含 MA5/MA10/MA20/MA60 均线），供前端绘图。

        period: daily / weekly / monthly。
        """
        try:
            hist = await data.get_history(symbol, period=period)
        except Exception as e:  # noqa: BLE001
            logger.exception("获取 K 线失败")
            raise HTTPException(status_code=500, detail=f"获取K线失败: {e}")

        df = hist.df.tail(days).reset_index(drop=True)
        close = df["close"]

        def ma(n: int) -> list:
            s = close.rolling(window=n, min_periods=n).mean()
            return [None if (isinstance(v, float) and math.isnan(v)) else round(float(v), 3) for v in s]

        klines = []
        for _, r in df.iterrows():
            klines.append({
                "date": str(r["date"]),
                "open": round(float(r["open"]), 3),
                "high": round(float(r["high"]), 3),
                "low": round(float(r["low"]), 3),
                "close": round(float(r["close"]), 3),
                "volume": float(r["volume"]) if "volume" in r and not (isinstance(r["volume"], float) and math.isnan(r["volume"])) else 0.0,
                "amount": float(r["amount"]) if "amount" in r and not (isinstance(r["amount"], float) and math.isnan(r["amount"])) else 0.0,
                "pct_chg": round(float(r["pctChg"]), 2) if "pctChg" in r and not (isinstance(r["pctChg"], float) and math.isnan(r["pctChg"])) else None,
            })
        return {
            "symbol": symbol,
            "name": getattr(hist, "name", symbol),
            "dates": [k["date"] for k in klines],
            "klines": klines,
            "ma5": ma(5),
            "ma10": ma(10),
            "ma20": ma(20),
            "ma60": ma(60),
        }

    @router.get("/stocks/{symbol}/realtime")
    async def stock_realtime(symbol: str):
        """返回个股盘中实时行情（腾讯），回退日频快照。"""
        if tencent is not None:
            try:
                q = await tencent.get_realtime_quote(symbol)
                if q:
                    return q
            except Exception as e:  # noqa: BLE001
                logger.warning("腾讯个股实时获取失败，回退 BaoStock: %s", e)
        try:
            q = await data.get_quote(symbol)
            return {
                "symbol": q.symbol, "name": q.name, "price": q.price,
                "preclose": None, "open": q.open, "change": q.change,
                "change_pct": q.change_pct, "high": q.high, "low": q.low,
                "volume": q.volume, "amount": q.amount, "timestamp": q.timestamp,
            }
        except Exception:  # noqa: BLE001
            return {}

    @router.get("/stocks/{symbol}/intraday")
    async def stock_intraday(symbol: str, period: str = "m5"):
        """返回个股分时/分钟K线（盘中）。period: m1 / m5。"""
        if tencent is not None:
            try:
                rows = await tencent.get_intraday(symbol, period=period)
                if rows:
                    return {
                        "symbol": symbol,
                        "period": period,
                        "times": [r["time"] for r in rows],
                        "klines": rows,
                    }
            except Exception as e:  # noqa: BLE001
                logger.warning("腾讯分时获取失败: %s", e)
        return {"symbol": symbol, "period": period, "times": [], "klines": []}

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
