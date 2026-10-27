"""数据层：股票数据接入抽象与实现。"""

from .provider import DataProvider, StockQuote, StockHistory
from .akshare_provider import AkshareProvider
from .baostock_provider import BaostockProvider
from .mock_provider import MockProvider
from .auto_provider import AutoProvider

__all__ = [
    "DataProvider", "StockQuote", "StockHistory",
    "AkshareProvider", "BaostockProvider", "MockProvider", "AutoProvider",
]
