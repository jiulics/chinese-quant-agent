"""编排器：串联数据获取 -> 多智能体辩论分析 -> 策略汇总。

流程：
1. 拉取行情与历史数据
2. 计算技术指标
3. 辩论引擎驱动多智能体（支持 5 级深度 + 多情景）
4. 输出最终中文投资信号（支持流式回调）
"""
from __future__ import annotations

import logging

from .data import DataProvider
from .debate import DebateEngine
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

    async def analyze(self, symbol: str, depth: int = 3, callback=None) -> dict:
        """对单只股票执行完整多智能体辩论式分析。

        depth: 1-5，控制辩论深度。
        callback: 可选异步回调，接收过程事件（用于 SSE）。
        """
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

        engine = DebateEngine(self.llm, callback=callback)
        debate_result = await engine.run(context, depth=depth)

        return {
            "symbol": symbol,
            "quote": quote,
            "indicators": indicators,
            "analyses": [a["content"] for a in debate_result["analyses"]],
            "analyses_structured": debate_result["analyses"],
            "scenarios": debate_result["scenarios"],
            "final_signal": debate_result["final_signal"],
            "depth": debate_result["depth"],
        }
