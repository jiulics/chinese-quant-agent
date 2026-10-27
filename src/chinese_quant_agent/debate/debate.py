"""辩论引擎：驱动多智能体辩论式分析，支持过程回调（用于 SSE 流式）。

职责：编排辩论流程（角色执行 -> 辩论轮次 -> 多情景 -> 最终信号）。
prompt 构造见 prompts.py，事件协议见 events.py，角色注册表见 registry.py。
"""
from __future__ import annotations

import logging
from typing import Any

from ..agents.base import AgentResult
from ..llm import LLMClient, LLMMessage
from .depth import get_depth_config
from .events import (
    Callback,
    agent_done_event,
    agent_delta_event,
    agent_start_event,
    final_event,
    stage_event,
)
from .moderator import ModeratorAgent, MultiScenarioAgent
from .prompts import build_prompt
from .registry import AGENT_CLASSES

logger = logging.getLogger(__name__)


class DebateEngine:
    """多智能体辩论引擎。"""

    def __init__(self, llm: LLMClient, callback: Callback | None = None) -> None:
        self.llm = llm
        self.callback = callback

    async def _emit(self, event: dict[str, Any]) -> None:
        if self.callback:
            await self.callback(event)

    async def _run_agent_stream(self, agent, context: dict, role_key: str) -> AgentResult:
        """流式运行单个 Agent，逐段回调增量。"""
        await self._emit(agent_start_event(role_key, agent.role))

        prompt = build_prompt(agent.role, context)

        parts: list[str] = []
        async for delta in self.llm.stream_chat(
            [LLMMessage("user", prompt)], system=agent.system_prompt
        ):
            parts.append(delta)
            await self._emit(agent_delta_event(role_key, delta))

        content = "".join(parts)
        await self._emit(agent_done_event(role_key, content))
        return AgentResult(role=agent.role, content=content)

    async def run(self, context: dict, depth: int = 3) -> dict:
        """执行辩论式分析，返回结构化结果。"""
        cfg = get_depth_config(depth)
        symbol = context.get("symbol", "未知")

        await self._emit(stage_event(
            f"深度{cfg.level} · {cfg.name}",
            f"开始对 {symbol} 进行{cfg.name}（{cfg.rounds} 轮辩论）",
        ))

        # 1. 按深度配置选择角色并流式运行
        analyses: list[AgentResult] = []
        for role_key in cfg.agents:
            if role_key == "moderator":
                continue
            agent = AGENT_CLASSES[role_key](self.llm)
            analyses.append(await self._run_agent_stream(agent, context, role_key))
        context["analyses"] = analyses

        # 2. 辩论轮次（主持人介入多轮）
        moderator = ModeratorAgent(self.llm)
        for round_i in range(cfg.rounds):
            await self._emit(stage_event(
                f"辩论第 {round_i + 1} 轮",
                f"主持人正在引导第 {round_i + 1} 轮观点交锋",
            ))
            analyses.append(await self._run_agent_stream(moderator, context, "moderator"))
            context["analyses"] = analyses

        # 3. 多情景观点（深度 >= 4 时启用）
        scenarios: str | None = None
        if cfg.include_multi_scenario:
            sc = await self._run_agent_stream(
                MultiScenarioAgent(self.llm), context, "scenario"
            )
            scenarios = sc.content

        # 4. 策略师汇总最终信号
        final = await self._run_agent_stream(
            AGENT_CLASSES["strategist"](self.llm), context, "strategist"
        )

        await self._emit(final_event(final.content))

        return {
            "depth": cfg.level,
            "analyses": [{"role": a.role, "content": a.content} for a in analyses],
            "scenarios": scenarios,
            "final_signal": final.content,
        }
