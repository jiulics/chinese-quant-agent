"""数据层：股票数据接入抽象与实现。"""

from .provider import DataProvider, StockQuote, StockHistory
from .akshare_provider import AkshareProvider
from .mock_provider import MockProvider

__all__ = ["DataProvider", "StockQuote", "StockHistory", "AkshareProvider", "MockProvider"]
