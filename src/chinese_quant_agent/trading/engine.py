"""模拟交易引擎：对接数据源，提供下单/行情/复盘。"""
from __future__ import annotations

import logging

from ..data import DataProvider
from .account import PaperAccount

logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """纸面交易引擎。"""

    def __init__(self, data: DataProvider, initial_cash: float = 1_000_000.0) -> None:
        self.data = data
        self.account = PaperAccount(initial_cash)

    async def _prices(self, symbols: list[str]) -> dict[str, float]:
        """获取多个标的最新价。"""
        prices: dict[str, float] = {}
        for sym in symbols:
            try:
                q = await self.data.get_quote(sym)
                prices[sym] = q.price
            except Exception as e:  # noqa: BLE001
                logger.warning("获取 %s 行情失败: %s", sym, e)
        return prices

    async def buy(self, symbol: str, quantity: int) -> dict:
        """买入。"""
        q = await self.data.get_quote(symbol)
        order = self.account.buy(symbol, q.name, q.price, quantity)
        return {"order": order, "price": q.price}

    async def sell(self, symbol: str, quantity: int) -> dict:
        """卖出。"""
        q = await self.data.get_quote(symbol)
        order = self.account.sell(symbol, q.price, quantity)
        return {"order": order, "price": q.price}

    async def snapshot(self) -> dict:
        """账户快照（含实时市值）。"""
        symbols = list(self.account.positions.keys())
        prices = await self._prices(symbols)
        return self.account.snapshot(prices)

    async def orders(self, limit: int = 50) -> list[dict]:
        """订单记录。"""
        return [
            {
                "order_id": o.order_id, "symbol": o.symbol, "name": o.name,
                "side": o.side, "price": o.price, "quantity": o.quantity,
                "status": o.status, "created_at": o.created_at,
            }
            for o in self.account.orders[-limit:][::-1]
        ]
