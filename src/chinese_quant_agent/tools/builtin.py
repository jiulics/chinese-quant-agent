"""内置工具集：行情查询、指标计算、股票搜索、记忆查询。"""
from __future__ import annotations

import logging
from typing import Any

from ..data import DataProvider
from ..indicators import compute_indicators
from ..memory import MemoryStore

logger = logging.getLogger(__name__)


def build_builtin_tools(
    data: DataProvider,
    memory: MemoryStore | None = None,
) -> list:
    """构建内置工具列表。"""
    from .base import Tool

    async def get_quote(symbol: str) -> str:
        """获取股票实时行情。"""
        q = await data.get_quote(symbol)
        return f"{q.name}({q.symbol}) 最新价:{q.price} 涨跌幅:{q.change_pct}%"

    async def get_indicators(symbol: str) -> str:
        """获取股票技术指标。"""
        hist = await data.get_history(symbol)
        ind = compute_indicators(hist.df)
        return str(ind)

    async def search_stocks(query: str) -> str:
        """搜索股票。"""
        items = await data.search_stocks(query, limit=10)
        return "; ".join(f"{it['symbol']} {it['name']}" for it in items)

    async def recall_facts(query: str) -> str:
        """从记忆中检索事实。"""
        if not memory:
            return "记忆系统未启用。"
        facts = await memory.list_facts(query, limit=10)
        if not facts:
            return "未找到相关事实。"
        return "\n".join(f"- {f['content']}" for f in facts)

    async def save_fact(content: str) -> str:
        """保存一条事实到记忆。"""
        if not memory:
            return "记忆系统未启用。"
        fid = await memory.add_fact(content, source="assistant")
        return f"已保存事实 #{fid}"

    return [
        Tool("get_quote", "获取某只股票的实时行情快照",
             {"type": "object", "properties": {"symbol": {"type": "string", "description": "股票代码，如 600519"}}, "required": ["symbol"]},
             get_quote),
        Tool("get_indicators", "获取某只股票的技术指标（MA/MACD/RSI/KDJ 等）",
             {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]},
             get_indicators),
        Tool("search_stocks", "按名称或代码搜索 A 股股票",
             {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
             search_stocks),
        Tool("recall_facts", "从 AI 记忆中检索已沉淀的事实",
             {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
             recall_facts),
        Tool("save_fact", "将一条重要事实保存到 AI 记忆",
             {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]},
             save_fact),
    ]
