"""数据层：股票数据接入抽象与实现。"""

from .provider import DataProvider, StockQuote, StockHistory

__all__ = ["DataProvider", "StockQuote", "StockHistory"]
