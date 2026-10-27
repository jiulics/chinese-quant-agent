"""风控 Agent。"""
from __future__ import annotations

from .base import Agent, AgentResult


class RiskAgent(Agent):
    role = "风控分析师"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名中文风控专家，负责仓位管理、止损与风险敞口评估。"
            "你的建议必须保守、量化，并始终提示'投资有风险'。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        quote = context.get("quote")
        prompt = (
            f"请对股票 {symbol} 做风险评估。\n"
            f"实时行情：{quote}\n"
            "请输出：1) 风险等级 2) 建议仓位 3) 止损位 4) 风险提示。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)
