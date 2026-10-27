"""Mock 数据源：当 akshare 网络不可用时自动降级，保证开发/演示可跑通。

数据为随机生成的近似真实走势，仅供开发与测试。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .provider import DataProvider, StockHistory, StockQuote

# 常见股票名称映射
_NAME_MAP = {
    "600519": "贵州茅台",
    "000001": "平安银行",
    "300750": "宁德时代",
    "601318": "中国平安",
    "600036": "招商银行",
    "000858": "五粮液",
    "601899": "紫金矿业",
    "600900": "长江电力",
}


class MockProvider(DataProvider):
    """随机 mock 数据源，用于网络不可用时的降级。"""

    def __init__(self, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)

    async def get_quote(self, symbol: str) -> StockQuote:
        base = self._rng.uniform(10, 2000)
        change_pct = self._rng.uniform(-5, 5)
        change = base * change_pct / 100
        return StockQuote(
            symbol=symbol,
            name=_NAME_MAP.get(symbol, f"股票{symbol}"),
            price=round(base, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2),
            open=round(base - change * 0.3, 2),
            high=round(base + abs(change) * 0.8, 2),
            low=round(base - abs(change) * 0.8, 2),
            volume=float(self._rng.integers(1e5, 1e7)),
            amount=float(self._rng.uniform(1e8, 1e10)),
            timestamp="2026-10-27",
        )

    async def get_history(self, symbol: str, *, start=None, end=None, period="daily") -> StockHistory:
        n = 120
        base = self._rng.uniform(10, 2000)
        close = base + np.cumsum(self._rng.normal(0, base * 0.01, n))
        close = np.clip(close, base * 0.5, base * 2)
        df = pd.DataFrame({
            "date": pd.date_range("2024-05-01", periods=n),
            "open": close - base * 0.005,
            "high": close + base * 0.01,
            "low": close - base * 0.01,
            "close": close,
            "volume": self._rng.integers(1e5, 1e7, n).astype(float),
            "amount": self._rng.uniform(1e8, 1e10, n),
        })
        return StockHistory(symbol=symbol, df=df)

    async def get_stock_list(self) -> pd.DataFrame:
        rows = [{"代码": k, "名称": v} for k, v in _NAME_MAP.items()]
        return pd.DataFrame(rows)

    async def search_stocks(self, query: str, limit: int = 20) -> list[dict[str, str]]:
        q = query.strip()
        return [
            {"symbol": k, "name": v}
            for k, v in _NAME_MAP.items()
            if q in k or q in v
        ][:limit]
