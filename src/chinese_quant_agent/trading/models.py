"""模拟交易数据模型。"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Order:
    """一笔订单。"""
    order_id: str
    symbol: str
    name: str
    side: str            # buy / sell
    price: float
    quantity: int
    status: str = "filled"   # filled / pending / cancelled
    created_at: float = field(default_factory=time.time)


@dataclass
class Position:
    """持仓。"""
    symbol: str
    name: str
    quantity: int
    avg_cost: float

    def market_value(self, price: float) -> float:
        return self.quantity * price

    def pnl(self, price: float) -> float:
        return (price - self.avg_cost) * self.quantity
