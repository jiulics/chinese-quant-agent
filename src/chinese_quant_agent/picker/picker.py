"""选股助手：按研究需求描述匹配候选股票池。

链路：自然语言需求 -> 筛选 -> 候选标的 -> LLM 智能推荐。
"""
from __future__ import annotations

import logging

from ..llm import LLMClient
from ..screener import Screener

logger = logging.getLogger(__name__)


class StockPicker:
    """选股助手。"""

    SYSTEM = (
        "你是一名中文选股助手，根据用户的投资研究需求，"
        "从候选股票池中推荐最匹配的标的并说明理由。"
        "务必附免责声明：内容仅供参考，不构成投资建议。"
    )

    def __init__(self, screener: Screener, llm: LLMClient) -> None:
        self.screener = screener
        self.llm = llm

    async def pick(self, need: str, callback=None) -> dict:
        """根据需求选股，返回 {need, candidates, recommendation}。"""
        await self._emit(callback, {"type": "stage", "message": "筛选候选股票池…"})

        # 1. 用 LLM 将需求翻译为筛选条件并筛选
        screen_result = await self.screener.natural_screen(need, callback=callback)
        candidates = screen_result.get("items", [])

        # 2. LLM 从候选中推荐
        await self._emit(callback, {"type": "stage", "message": "智能匹配候选标的…"})

        if not candidates:
            recommendation = "未找到匹配的候选标的，请调整需求描述。"
        else:
            pool = "\n".join(
                f"{i+1}. {c.get('name','')}({c.get('symbol','')})"
                + (f" 价格:{c.get('price','')} 涨跌幅:{c.get('change_pct','')}%" if 'price' in c else "")
                for i, c in enumerate(candidates[:20])
            )
            prompt = (
                f"用户研究需求：{need}\n\n候选股票池：\n{pool}\n\n"
                "请推荐最匹配的 3-5 只标的，说明推荐理由与风险。"
            )
            resp = await self.llm.complete(prompt, system=self.SYSTEM)
            recommendation = resp.content

        await self._emit(callback, {"type": "done", "recommendation": recommendation})
        return {
            "need": need,
            "candidates": candidates,
            "recommendation": recommendation,
        }

    async def _emit(self, callback, event: dict) -> None:
        if callback:
            await callback(event)
