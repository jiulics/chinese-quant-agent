"""库级入口：便捷地构建并运行一次分析。"""
from __future__ import annotations

import asyncio

from config.settings import get_settings

from .data.akshare_provider import AkshareProvider
from .llm import build_client_from_settings
from .orchestrator import Orchestrator


async def analyze_stock(symbol: str) -> dict:
    """对单只股票执行多智能体分析，返回结构化结果。"""
    settings = get_settings()
    llm = build_client_from_settings(settings)
    data = AkshareProvider()
    orch = Orchestrator(llm=llm, data=data)
    return await orch.analyze(symbol)


def analyze_stock_sync(symbol: str) -> dict:
    """同步便捷入口。"""
    return asyncio.run(analyze_stock(symbol))
