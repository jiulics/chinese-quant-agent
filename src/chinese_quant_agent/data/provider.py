"""数据提供者抽象接口。

定义统一的股票数据模型与接口，方便替换数据源（akshare / tushare / 自建）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass
class StockQuote:
    """实时行情快照。"""

    symbol: str          # 股票代码，如 "600519"
    name: str            # 股票名称，如 "贵州茅台"
    price: float         # 最新价
    change: float        # 涨跌额
    change_pct: float    # 涨跌幅（%）
    open: float          # 今开
    high: float          # 最高
    low: float           # 最低
    volume: float        # 成交量
    amount: float        # 成交额
    timestamp: str       # 时间戳


@dataclass
class StockHistory:
    """历史 K 线数据。"""

    symbol: str
    df: pd.DataFrame     # 列：date, open, high, low, close, volume, amount


class DataProvider(ABC):
    """股票数据提供者抽象基类。"""

    @abstractmethod
    async def get_quote(self, symbol: str) -> StockQuote:
        """获取单只股票实时行情。"""

    @abstractmethod
    async def get_history(
        self,
        symbol: str,
        *,
        start: str | None = None,
        end: str | None = None,
        period: str = "daily",
    ) -> StockHistory:
        """获取历史 K 线。

        period: daily / weekly / monthly。
        """

    @abstractmethod
    async def get_stock_list(self) -> pd.DataFrame:
        """获取 A 股股票列表（代码、名称）。"""

    async def get_indices(self) -> list[dict]:
        """获取主要大盘指数快照。默认返回空列表，子类按需覆盖。"""
        return []

    async def get_valuation_data(self, symbol: str) -> dict:
        """获取估值指标（PE/PB/PS/PCF）。默认返回空，子类按需覆盖。"""
        return {}

    async def get_financial_data(self, symbol: str) -> dict:
        """获取财务数据（盈利/成长/偿债）。默认返回空，子类按需覆盖。"""
        return {}
