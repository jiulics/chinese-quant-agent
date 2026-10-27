"""策略/信号 Agent：汇总各分析并生成最终中文投资信号。"""
from __future__ import annotations

from .base import Agent, AgentResult


class StrategistAgent(Agent):
    role = "策略师"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名中文量化策略师，负责综合各维度分析，"
            "输出结构化的投资信号（看多/看空/观望）与操作建议。"
            "必须附上免责声明：内容仅供参考，不构成投资建议。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        analyses = context.get("analyses", [])
        summary = "\n\n".join(
            f"[{a.role}]\n{a.content}" for a in analyses
        )
        prompt = (
            f"请综合以下对股票 {symbol} 的分析，给出最终投资信号：\n\n{summary}\n\n"
            "请输出：1) 综合结论（看多/看空/观望）2) 核心逻辑 3) 操作建议 4) 免责声明。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)
