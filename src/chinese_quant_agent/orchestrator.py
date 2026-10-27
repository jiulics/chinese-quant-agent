"""编排器：串联数据获取 -> 多智能体分析 -> 策略汇总。

流程：
1. 拉取行情与历史数据
2. 计算技术指标
3. 并行运行分析师 / 技术面 / 风控 Agent
4. 策略师汇总生成最终中文投资信号
"""
from __future__ import annotations

import asyncio
import logging

from .agents import AnalystAgent, RiskAgent, StrategistAgent, TechnicalAgent
from .data import DataProvider
from .indicators import compute_indicators
from .llm import LLMClient
from .memory import SharedMemory

logger = logging.getLogger(__name__)


class Orchestrator:
    """多智能体交易分析编排器。"""

    def __init__(
        self,
        llm: LLMClient,
        data: DataProvider,
        memory: SharedMemory | None = None,
    ) -> None:
        self.llm = llm
        self.data = data
        self.memory = memory or SharedMemory()

    async def analyze(self, symbol: str) -> dict:
        """对单只股票执行完整多智能体分析。"""
        # 1. 数据
        quote = await self.data.get_quote(symbol)
        history = await self.data.get_history(symbol)
        indicators = compute_indicators(history.df)

        context = {
            "symbol": symbol,
            "quote": quote,
            "history": history,
            "indicators": indicators,
        }
        self.memory.update(**context)

        # 2. 并行运行三个分析 Agent
        analyst = AnalystAgent(self.llm)
        technical = TechnicalAgent(self.llm)
        risk = RiskAgent(self.llm)

        results = await asyncio.gather(
            analyst.run(context),
            technical.run(context),
            risk.run(context),
        )

        # 3. 策略师汇总
        strategist = StrategistAgent(self.llm)
        context["analyses"] = list(results)
        final = await strategist.run(context)

        return {
            "symbol": symbol,
            "quote": quote,
            "indicators": indicators,
            "analyses": [r.content for r in results],
            "final_signal": final.content,
        }
