"""akshare 数据源实现（免费、无需 token）。

akshare 是同步库，这里用 asyncio.to_thread 包一层以适配异步接口。
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

import akshare as ak
import pandas as pd

from .provider import DataProvider, StockHistory, StockQuote

logger = logging.getLogger(__name__)


def _normalize_symbol(symbol: str) -> str:
    """去除可能的前后缀，保留纯数字代码。"""
    return symbol.strip().lower().replace("sh", "").replace("sz", "").replace(".", "")


class AkshareProvider(DataProvider):
    """基于 akshare 的 A 股数据源。"""

    async def get_quote(self, symbol: str) -> StockQuote:
        code = _normalize_symbol(symbol)
        df = await asyncio.to_thread(
            lambda: ak.stock_zh_a_spot_em()  # 东方财富全市场快照
        )
        row = df[df["代码"] == code]
        if row.empty:
            raise ValueError(f"未找到股票代码: {symbol}")

        r = row.iloc[0]
        return StockQuote(
            symbol=code,
            name=str(r["名称"]),
            price=float(r["最新价"]),
            change=float(r["涨跌额"]),
            change_pct=float(r["涨跌幅"]),
            open=float(r["今开"]),
            high=float(r["最高"]),
            low=float(r["最低"]),
            volume=float(r["成交量"]),
            amount=float(r["成交额"]),
            timestamp=str(r.get("数据日期", "")),
        )

    async def get_history(
        self,
        symbol: str,
        *,
        start: str | None = None,
        end: str | None = None,
        period: str = "daily",
    ) -> StockHistory:
        code = _normalize_symbol(symbol)
        adjust = ""  # 不复权
        df = await asyncio.to_thread(
            lambda: ak.stock_zh_a_hist(
                symbol=code,
                period=period,
                start_date=start or "20200101",
                end_date=end or "20500101",
                adjust=adjust,
            )
        )
        if df is None or df.empty:
            raise ValueError(f"未获取到历史数据: {symbol}")

        # 统一列名
        rename = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
        }
        df = df.rename(columns=rename)
        keep = ["date", "open", "high", "low", "close", "volume", "amount"]
        df = df[[c for c in keep if c in df.columns]]
        for c in ["open", "high", "low", "close", "volume", "amount"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return StockHistory(symbol=code, df=df)

    async def get_stock_list(self) -> pd.DataFrame:
        df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
        return df[["代码", "名称"]].copy()
