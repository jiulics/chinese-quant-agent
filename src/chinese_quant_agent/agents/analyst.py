"""基本面分析师 Agent。"""
from __future__ import annotations

from .base import Agent, AgentResult


class AnalystAgent(Agent):
    role = "基本面分析师"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名资深的中文基本面分析师，专注于 A 股个股分析。"
            "请基于提供的行情与基本面数据，从公司业务、估值、行业地位等角度"
            "给出客观、审慎的中文分析，并明确说明分析依据与不确定性。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        quote = context.get("quote")
        prompt = (
            f"请分析股票 {symbol}。\n"
            f"实时行情：{quote}\n"
            "请输出：1) 基本面概览 2) 估值判断 3) 主要风险。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)
