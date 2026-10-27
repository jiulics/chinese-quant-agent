"""API 请求/响应模型。"""
from __future__ import annotations

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    symbol: str
    depth: int = 3  # 深度等级 1-5


class QuoteOut(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    volume: float
    amount: float
    timestamp: str


class AnalyzeResponse(BaseModel):
    symbol: str
    quote: QuoteOut
    indicators: dict
    analyses: list[str]
    final_signal: str


class StockItem(BaseModel):
    symbol: str
    name: str
