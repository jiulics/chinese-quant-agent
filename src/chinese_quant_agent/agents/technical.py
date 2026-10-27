"""技术面分析师 Agent。"""
from __future__ import annotations

from .base import Agent, AgentResult


class TechnicalAgent(Agent):
    role = "技术面分析师"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名中文技术分析专家，精通 K 线、均线、MACD、RSI、KDJ 等技术指标。"
            "请基于历史行情与技术指标，给出趋势、支撑阻力与买卖点判断，语言客观。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        indicators = context.get("indicators", {})
        prompt = (
            f"请对股票 {symbol} 做技术面分析。\n"
            f"技术指标：{indicators}\n"
            "请输出：1) 趋势判断 2) 关键支撑/阻力位 3) 技术信号。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)
