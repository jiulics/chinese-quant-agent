"""API 请求/响应模型。"""
from __future__ import annotations

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    symbol: str
    depth: int = 3  # 深度等级 1-5
    use_mock: bool = False  # 是否强制使用 mock 数据


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
    valuation: dict = {}
    financials: dict = {}
    analyses: list[str]
    scenarios: str | None = None
    final_signal: str
    depth: int


class StockItem(BaseModel):
    symbol: str
    name: str
