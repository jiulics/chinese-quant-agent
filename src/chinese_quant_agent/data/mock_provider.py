"""Mock 数据源：当 akshare 网络不可用时自动降级，保证开发/演示可跑通。

数据为随机生成的近似真实走势，仅供开发与测试。
为保持会话内一致性，同一股票的价格按 symbol 确定性生成并稳定。
"""
from __future__ import annotations

import hashlib

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
    "600000": "浦发银行",
    "000002": "万科A",
    "002594": "比亚迪",
    "601012": "隆基绿能",
}

# 常见股票的确定性基准价（更接近真实，便于演示）
_BASE_PRICE = {
    "600519": 1550.0,
    "000001": 11.5,
    "300750": 180.0,
    "601318": 48.0,
    "600036": 38.0,
    "000858": 140.0,
    "601899": 17.0,
    "600900": 28.0,
    "600000": 10.0,
    "000002": 8.5,
    "002594": 250.0,
    "601012": 20.0,
}


def _deterministic_price(symbol: str) -> tuple[float, float]:
    """按 symbol 生成确定性的价格与涨跌幅，保证多次调用一致。"""
    base = _BASE_PRICE.get(symbol)
    if base is None:
        # 未收录的股票用哈希生成稳定基准价
        h = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
        base = round(5 + (h % 2000) / 10, 2)
    # 稳定涨跌幅
    h2 = int(hashlib.md5((symbol + "pct").encode()).hexdigest()[:8], 16)
    change_pct = round((h2 % 1000) / 100 - 5, 2)  # -5 ~ +5
    change = round(base * change_pct / 100, 2)
    return base, change_pct, change


class MockProvider(DataProvider):
    """确定性 mock 数据源，用于网络不可用时的降级与演示。"""

    def __init__(self, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)

    async def get_quote(self, symbol: str) -> StockQuote:
        base, change_pct, change = _deterministic_price(symbol)
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
        base, _, _ = _deterministic_price(symbol)
        rng = np.random.default_rng(hash(symbol) % (2**32))
        close = base + np.cumsum(rng.normal(0, base * 0.01, n))
        close = np.clip(close, base * 0.5, base * 2)
        df = pd.DataFrame({
            "date": pd.date_range("2024-05-01", periods=n),
            "open": close - base * 0.005,
            "high": close + base * 0.01,
            "low": close - base * 0.01,
            "close": close,
            "volume": rng.integers(1e5, 1e7, n).astype(float),
            "amount": rng.uniform(1e8, 1e10, n),
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
