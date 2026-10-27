"""通用研究：对任意市场主题做开放式研究（不限单只股票）。"""
from __future__ import annotations

import logging

from ..llm import LLMClient, LLMMessage

logger = logging.getLogger(__name__)


class GeneralResearcher:
    """通用研究员：自然语言提问，研究行业/板块/宏观/个股对比等。"""

    SYSTEM = (
        "你是一名中文金融市场研究员，擅长行业、板块、宏观与个股对比研究。"
        "回答结构清晰、有理有据，并注明信息来源与不确定性。"
        "涉及投资建议时附免责声明：内容仅供参考，不构成投资建议。"
    )

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def research(self, topic: str, callback=None) -> dict:
        """研究一个主题，返回 {topic, content}。"""
        await self._emit(callback, {"type": "stage", "message": f"开始研究主题：{topic}"})

        prompt = (
            f"请研究以下主题，给出结构化报告：\n\n{topic}\n\n"
            "请包含：1) 主题概述 2) 关键要点分析 3) 相关标的或数据 4) 风险提示。"
        )
        parts: list[str] = []
        async for delta in self.llm.stream_chat([LLMMessage("user", prompt)], system=self.SYSTEM):
            parts.append(delta)
            await self._emit(callback, {"type": "delta", "delta": delta})

        content = "".join(parts)
        await self._emit(callback, {"type": "done", "content": content})
        return {"topic": topic, "content": content}

    async def _emit(self, callback, event: dict) -> None:
        if callback:
            await callback(event)
