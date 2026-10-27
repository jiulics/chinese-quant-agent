"""模拟交易账户：现金、持仓、订单与成交管理。"""
from __future__ import annotations

import logging
import time
import uuid

from .models import Order, Position

logger = logging.getLogger(__name__)


class PaperAccount:
    """纸面交易账户。"""

    def __init__(self, initial_cash: float = 1_000_000.0) -> None:
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: dict[str, Position] = {}
        self.orders: list[Order] = []

    def buy(self, symbol: str, name: str, price: float, quantity: int) -> Order:
        """买入。"""
        cost = price * quantity
        if cost > self.cash:
            raise ValueError(f"现金不足：需要 {cost:.2f}，可用 {self.cash:.2f}")
        self.cash -= cost

        pos = self.positions.get(symbol)
        if pos:
            total_qty = pos.quantity + quantity
            pos.avg_cost = (pos.avg_cost * pos.quantity + cost) / total_qty
            pos.quantity = total_qty
        else:
            self.positions[symbol] = Position(symbol, name, quantity, price)

        order = Order(uuid.uuid4().hex[:10], symbol, name, "buy", price, quantity)
        self.orders.append(order)
        return order

    def sell(self, symbol: str, price: float, quantity: int) -> Order:
        """卖出。"""
        pos = self.positions.get(symbol)
        if not pos or pos.quantity < quantity:
            raise ValueError(f"持仓不足：{symbol} 当前 {pos.quantity if pos else 0} 股")
        self.cash += price * quantity
        pos.quantity -= quantity
        if pos.quantity == 0:
            del self.positions[symbol]

        order = Order(uuid.uuid4().hex[:10], symbol, pos.name, "sell", price, quantity)
        self.orders.append(order)
        return order

    def total_value(self, prices: dict[str, float]) -> float:
        """总资产 = 现金 + 持仓市值。"""
        mv = sum(p.market_value(prices.get(sym, p.avg_cost)) for sym, p in self.positions.items())
        return self.cash + mv

    def total_pnl(self, prices: dict[str, float]) -> float:
        """浮动盈亏。"""
        return sum(p.pnl(prices.get(sym, p.avg_cost)) for sym, p in self.positions.items())

    def snapshot(self, prices: dict[str, float]) -> dict:
        """账户快照。"""
        positions = [
            {
                "symbol": p.symbol,
                "name": p.name,
                "quantity": p.quantity,
                "avg_cost": round(p.avg_cost, 3),
                "price": round(prices.get(p.symbol, p.avg_cost), 3),
                "pnl": round(p.pnl(prices.get(p.symbol, p.avg_cost)), 2),
            }
            for p in self.positions.values()
        ]
        return {
            "cash": round(self.cash, 2),
            "initial_cash": self.initial_cash,
            "market_value": round(self.total_value(prices), 2),
            "total_pnl": round(self.total_pnl(prices), 2),
            "total_return_pct": round((self.total_value(prices) / self.initial_cash - 1) * 100, 2),
            "positions": positions,
        }
