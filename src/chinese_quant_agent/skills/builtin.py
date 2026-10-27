"""内置技能：示例数据获取技能，供 Skill 中心展示与扩展。"""
from __future__ import annotations

from ..data import DataProvider
from .manager import Skill, SkillManager


def build_builtin_skills(data: DataProvider) -> SkillManager:
    """构建内置技能集。"""
    mgr = SkillManager()

    async def get_quote(symbol: str) -> str:
        q = await data.get_quote(symbol)
        return f"{q.name}({q.symbol}) 价格 {q.price} 涨跌幅 {q.change_pct}%"

    async def get_history_summary(symbol: str, days: int = 30) -> str:
        hist = await data.get_history(symbol)
        df = hist.df.tail(days)
        return (
            f"{symbol} 近 {days} 日："
            f"最高 {df['high'].max():.2f}，最低 {df['low'].min():.2f}，"
            f"最新 {df['close'].iloc[-1]:.2f}"
        )

    async def list_top_stocks(limit: int = 10) -> str:
        df = await data.get_stock_list()
        return "\n".join(f"{r['代码']} {r['名称']}" for _, r in df.head(limit).iterrows())

    mgr.register(Skill(
        "get_quote", "获取单只股票实时行情快照",
        {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]},
        get_quote,
    ))
    mgr.register(Skill(
        "get_history_summary", "获取股票近 N 日行情摘要（最高/最低/最新价）",
        {"type": "object", "properties": {"symbol": {"type": "string"}, "days": {"type": "integer"}}, "required": ["symbol"]},
        get_history_summary,
    ))
    mgr.register(Skill(
        "list_top_stocks", "列出股票池前 N 只股票",
        {"type": "object", "properties": {"limit": {"type": "integer"}}},
        list_top_stocks,
    ))
    return mgr
