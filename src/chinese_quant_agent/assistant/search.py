"""联网搜索：为智能助手提供外部信息检索能力。

默认提供 DuckDuckGo 搜索；可扩展接入其他搜索 API。
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WebSearch:
    """联网搜索抽象。"""

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """搜索并返回 [{title, url, snippet}, ...]。"""
        raise NotImplementedError


class DuckDuckGoSearch(WebSearch):
    """基于 DuckDuckGo 的联网搜索（无需 API Key）。"""

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        try:
            import httpx
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("未安装 duckduckgo_search，联网搜索不可用")
            return []

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=limit))
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in results
            ]
        except Exception as e:  # noqa: BLE001
            logger.warning("联网搜索失败: %s", e)
            return []


def build_search_tool(search: WebSearch):
    """将联网搜索包装为工具，供 function calling 调用。"""
    from ..tools.base import Tool

    async def web_search(query: str) -> str:
        results = await search.search(query, limit=5)
        if not results:
            return "未获取到搜索结果。"
        return "\n".join(f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results)

    return Tool(
        "web_search", "联网搜索获取实时外部信息",
        {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        web_search,
    )
