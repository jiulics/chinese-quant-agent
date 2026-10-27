"""多源自动回退数据提供器。

优先级：BaoStock（真实免费） -> AKShare（真实） -> Mock（降级）。
任何一层失败自动回退到下一层，保证始终能返回数据，
同时优先使用真实行情。回退记录在日志中。
"""
from __future__ import annotations

import logging

import pandas as pd

from .baostock_provider import BaostockProvider
from .akshare_provider import AkshareProvider
from .mock_provider import MockProvider
from .provider import DataProvider, StockHistory, StockQuote

logger = logging.getLogger(__name__)


class AutoProvider(DataProvider):
    """多源自动回退数据源。"""

    def __init__(self) -> None:
        self._stock_list_cache: pd.DataFrame | None = None
        self._baostock = BaostockProvider()
        self._akshare = AkshareProvider()
        self._mock = MockProvider()
        # 优先顺序
        self._chain: list[DataProvider] = [
            p for p in (self._baostock, self._akshare)
            if getattr(p, "available", True)
        ] + [self._mock]

    @property
    def active_source(self) -> str:
        """当前实际生效的数据源名。"""
        return self._chain[0].__class__.__name__

    async def get_quote(self, symbol: str) -> StockQuote:
        for p in self._chain:
            try:
                return await p.get_quote(symbol)
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取 %s 行情失败，回退: %s", p.__class__.__name__, symbol, e)
        # 理论上 mock 不会失败，兜底
        return await self._mock.get_quote(symbol)

    async def get_history(self, symbol: str, **kwargs) -> StockHistory:
        for p in self._chain:
            try:
                return await p.get_history(symbol, **kwargs)
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取 %s 历史失败，回退: %s", p.__class__.__name__, symbol, e)
        return await self._mock.get_history(symbol, **kwargs)

    async def get_stock_list(self) -> pd.DataFrame:
        if self._stock_list_cache is not None:
            return self._stock_list_cache
        for p in self._chain:
            try:
                df = await p.get_stock_list()
                if len(df) > 0:
                    self._stock_list_cache = df
                    return df
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取股票列表失败，回退: %s", p.__class__.__name__, e)
        return await self._mock.get_stock_list()

    async def get_indices(self) -> list[dict]:
        for p in self._chain:
            try:
                result = await p.get_indices()
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取指数失败，回退: %s", p.__class__.__name__, e)
        return []

    async def get_valuation_data(self, symbol: str) -> dict:
        for p in self._chain:
            try:
                result = await p.get_valuation_data(symbol)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取估值失败，回退: %s", p.__class__.__name__, e)
        return {}

    async def get_financial_data(self, symbol: str) -> dict:
        for p in self._chain:
            try:
                result = await p.get_financial_data(symbol)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 获取财务失败，回退: %s", p.__class__.__name__, e)
        return {}

    async def search_stocks(self, query: str, limit: int = 20) -> list[dict[str, str]]:
        for p in self._chain:
            try:
                result = await p.search_stocks(query, limit)
                if result:
                    return result
            except Exception as e:  # noqa: BLE001
                logger.warning("%s 搜索失败，回退: %s", p.__class__.__name__, e)
        return await self._mock.search_stocks(query, limit)
