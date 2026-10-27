"""事实抽取器：用 LLM 从研究文本中抽取并结构化关键事实。

抽取结果沉淀到 MemoryStore，实现"事实记忆"。
"""
from __future__ import annotations

import json
import logging
import re

from ..llm import LLMClient, LLMMessage

logger = logging.getLogger(__name__)


class FactExtractor:
    """从分析文本中抽取关键事实。"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def extract(self, text: str, symbol: str = "") -> list[dict]:
        """从一段分析文本中抽取事实，返回 [{content, tags}, ...]。

        若 LLM 调用失败，降级为基于句子的启发式抽取。
        """
        prompt = (
            "请从以下金融分析文本中抽取关键事实，每条事实必须客观、简洁、可独立理解。\n"
            "只输出 JSON 数组，每项形如 {\"content\": \"事实内容\", \"tags\": [\"标签\"]}。\n"
            f"标的：{symbol}\n\n分析文本：\n{text}"
        )
        try:
            resp = await self.llm.complete(prompt, system="你是金融事实抽取助手。")
            facts = self._parse_json(resp.content)
            if facts:
                return facts
        except Exception as e:  # noqa: BLE001
            logger.warning("事实抽取 LLM 调用失败，降级启发式: %s", e)
        return self._heuristic(text, symbol)

    def _parse_json(self, content: str) -> list[dict]:
        """从 LLM 输出中稳健解析 JSON 数组。"""
        m = re.search(r"\[.*\]", content, re.S)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict) and d.get("content")]
        except json.JSONDecodeError:
            return []
        return []

    def _heuristic(self, text: str, symbol: str) -> list[dict]:
        """启发式：按句号切分，取含数字或关键词的句子作为事实。"""
        keywords = ["市值", "PE", "PB", "ROE", "营收", "净利润", "毛利率", "股价", "支撑", "阻力"]
        facts = []
        for sent in re.split(r"[。；\n]", text):
            sent = sent.strip()
            if len(sent) < 8 or len(sent) > 120:
                continue
            if any(k in sent for k in keywords):
                facts.append({"content": sent, "tags": [symbol] if symbol else []})
        return facts[:10]
