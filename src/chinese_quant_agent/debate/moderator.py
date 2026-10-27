"""辩论主持人 Agent：引导多轮观点碰撞，并输出多情景综合结论。"""
from __future__ import annotations

from ..agents.base import Agent, AgentResult


class ModeratorAgent(Agent):
    role = "辩论主持人"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名资深的投资研究辩论主持人，擅长引导不同观点的分析师"
            "就关键分歧点展开多轮交锋，并最终收敛出均衡、审慎的结论。"
            "你必须指出各方观点的矛盾与互补之处，避免一边倒。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        analyses = context.get("analyses", [])
        transcript = "\n\n".join(f"[{a.role}]\n{a.content}" for a in analyses)
        prompt = (
            f"以下是关于股票 {symbol} 的多位分析师观点：\n\n{transcript}\n\n"
            "请作为主持人：1) 指出各方核心分歧点 2) 对分歧做裁决或折中 "
            "3) 给出多情景（牛市/震荡/熊市）下的差异化观点 4) 总结均衡结论。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)


class MultiScenarioAgent(Agent):
    """多情景观点呈现：牛/熊/震荡三情景分析。"""

    role = "情景分析师"

    @property
    def system_prompt(self) -> str:
        return (
            "你是一名中文宏观情景分析专家。请针对同一标的，"
            "分别从牛市、震荡市、熊市三种情景给出差异化、可操作的观点，"
            "并明确每种情景的触发条件。"
        )

    async def run(self, context: dict) -> AgentResult:
        symbol = context.get("symbol", "未知")
        quote = context.get("quote")
        prompt = (
            f"请对股票 {symbol} 做多情景分析。\n"
            f"当前行情：{quote}\n\n"
            "请分别输出【牛市情景】【震荡情景】【熊市情景】下的观点，"
            "每种情景说明：触发条件、核心逻辑、操作建议。"
        )
        resp = await self.llm.complete(prompt, system=self.system_prompt)
        return AgentResult(role=self.role, content=resp.content)
