"""股票筛选：自然语言 + 条件筛选相结合，从 A 股中发现标的。

条件筛选基于数据源返回的股票列表与行情/指标，做多维度过滤。
自然语言筛选由 LLM 将需求翻译为筛选条件后复用条件筛选引擎。
"""
from __future__ import annotations

import logging
from typing import Any

from ..data import DataProvider
from ..llm import LLMClient, LLMMessage

logger = logging.getLogger(__name__)


class Screener:
    """股票筛选器。"""

    def __init__(self, data: DataProvider, llm: LLMClient | None = None) -> None:
        self.data = data
        self.llm = llm

    async def screen(self, criteria: dict) -> dict:
        """按结构化条件筛选。

        criteria 支持：
            industry: 行业关键词
            min_price / max_price: 价格区间
            min_pct / max_pct: 涨跌幅区间
            keyword: 名称/代码关键词
            limit: 返回数量
        """
        limit = criteria.get("limit", 50)
        try:
            df = await self.data.get_stock_list()
        except Exception:  # noqa: BLE001
            return {"items": [], "total": 0, "error": "数据源不可用"}

        items: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            symbol = str(row.get("代码", row.get("symbol", "")))
            name = str(row.get("名称", row.get("name", "")))
            item = {"symbol": symbol, "name": name}

            # 关键词过滤
            kw = criteria.get("keyword", "")
            if kw and kw not in symbol and kw not in name:
                continue

            # 行业过滤（akshare 列表通常无行业列，用名称模糊匹配）
            industry = criteria.get("industry", "")
            if industry and industry not in name:
                continue

            # 价格/涨跌幅过滤需拉行情，这里对 mock 数据直接生成
            if any(k in criteria for k in ("min_price", "max_price", "min_pct", "max_pct")):
                try:
                    q = await self.data.get_quote(symbol)
                except Exception:  # noqa: BLE001
                    continue
                price = q.price
                pct = q.change_pct
                if "min_price" in criteria and price < criteria["min_price"]:
                    continue
                if "max_price" in criteria and price > criteria["max_price"]:
                    continue
                if "min_pct" in criteria and pct < criteria["min_pct"]:
                    continue
                if "max_pct" in criteria and pct > criteria["max_pct"]:
                    continue
                item["price"] = price
                item["change_pct"] = pct

            items.append(item)
            if len(items) >= limit:
                break

        return {"items": items, "total": len(items)}

    async def natural_screen(self, query: str, callback=None) -> dict:
        """自然语言筛选：LLM 翻译为条件，再执行筛选。"""
        if not self.llm:
            return {"items": [], "total": 0, "error": "未配置 LLM"}

        await self._emit(callback, {"type": "stage", "message": "解析筛选需求…"})

        prompt = (
            "将以下自然语言筛选需求翻译为 JSON 条件，可用的键："
            "keyword(名称/代码关键词)、industry(行业)、min_price、max_price、"
            "min_pct、max_pct、limit(默认50)。只输出 JSON。\n\n需求：{query}"
        )
        resp = await self.llm.complete(prompt.format(query=query), system="你是筛选条件解析助手。")
        criteria = self._parse_json(resp.content)
        await self._emit(callback, {"type": "criteria", "criteria": criteria})

        result = await self.screen(criteria)
        await self._emit(callback, {"type": "done", **result})
        return result

    def _parse_json(self, content: str) -> dict:
        import json
        import re
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            return {}
        try:
            data = json.loads(m.group(0))
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    async def _emit(self, callback, event: dict) -> None:
        if callback:
            await callback(event)
