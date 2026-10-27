"""各角色 Agent 的输入 prompt 构造。

将 prompt 逻辑从引擎中抽离，便于单独维护与测试。
同时负责把行情/指标等结构化数据格式化为 LLM 易读的文本。
"""
from __future__ import annotations

import math
from typing import Any


def _fmt_num(v: Any, nd: int = 2) -> str:
    """格式化数字，NaN/None 显示为 '-'。"""
    if v is None:
        return "-"
    try:
        f = float(v)
        if math.isnan(f):
            return "-"
        return f"{f:.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


def _fmt_quote(quote: Any) -> str:
    """格式化行情快照为简洁可读文本。"""
    if quote is None:
        return "（无实时行情）"
    if hasattr(quote, "price"):  # StockQuote dataclass
        return (
            f"{getattr(quote, 'name', '')}（{getattr(quote, 'symbol', '')}）"
            f"最新价 {_fmt_num(getattr(quote, 'price', None))}，"
            f"涨跌 {_fmt_num(getattr(quote, 'change', None))}"
            f"（{_fmt_num(getattr(quote, 'change_pct', None))}%），"
            f"今开 {_fmt_num(getattr(quote, 'open', None))}，"
            f"最高 {_fmt_num(getattr(quote, 'high', None))}，"
            f"最低 {_fmt_num(getattr(quote, 'low', None))}，"
            f"成交量 {_fmt_num(getattr(quote, 'volume', None), 0)}，"
            f"成交额 {_fmt_num(getattr(quote, 'amount', None), 0)}"
        )
    return str(quote)


def _fmt_indicators(ind: dict) -> str:
    """格式化技术指标字典为紧凑可读文本。"""
    if not ind:
        return "（无技术指标）"
    parts = []
    for k, v in ind.items():
        if k == "近5日收盘":
            parts.append(f"{k}: [{', '.join(_fmt_num(x) for x in v)}]")
        else:
            parts.append(f"{k}: {_fmt_num(v)}")
    return "；".join(parts)


def build_prompt(role: str, context: dict) -> str:
    """根据角色名构造输入 prompt。"""
    symbol = context.get("symbol", "未知")
    quote = _fmt_quote(context.get("quote"))
    indicators = _fmt_indicators(context.get("indicators", {}))

    if role == "基本面分析师":
        return (
            f"请分析股票 {symbol}。\n实时行情：{quote}\n"
            "请输出：1) 基本面概览 2) 估值判断 3) 主要风险。"
        )
    if role == "技术面分析师":
        return (
            f"请对股票 {symbol} 做技术面分析。\n技术指标：{indicators}\n"
            "请输出：1) 趋势判断 2) 关键支撑/阻力位 3) 技术信号。"
        )
    if role == "风控分析师":
        return (
            f"请对股票 {symbol} 做风险评估。\n实时行情：{quote}\n"
            "请输出：1) 风险等级 2) 建议仓位 3) 止损位 4) 风险提示。"
        )
    if role == "策略师":
        return _build_summary_prompt(symbol, context)
    if role == "辩论主持人":
        return _build_moderator_prompt(symbol, context)
    if role == "情景分析师":
        return (
            f"请对股票 {symbol} 做多情景分析。\n当前行情：{quote}\n\n"
            "请分别输出【牛市情景】【震荡情景】【熊市情景】下的观点，"
            "每种情景说明：触发条件、核心逻辑、操作建议。"
        )
    return f"请分析股票 {symbol}。"


def _build_summary_prompt(symbol: str, context: dict) -> str:
    analyses = context.get("analyses", [])
    summary = "\n\n".join(f"[{a.role}]\n{a.content}" for a in analyses)
    return (
        f"请综合以下对股票 {symbol} 的分析，给出最终投资信号：\n\n{summary}\n\n"
        "请输出：1) 综合结论（看多/看空/观望）2) 核心逻辑 3) 操作建议 4) 免责声明。"
    )


def _build_moderator_prompt(symbol: str, context: dict) -> str:
    analyses = context.get("analyses", [])
    transcript = "\n\n".join(f"[{a.role}]\n{a.content}" for a in analyses)
    return (
        f"以下是关于股票 {symbol} 的多位分析师观点：\n\n{transcript}\n\n"
        "请作为主持人：1) 指出各方核心分歧点 2) 对分歧做裁决或折中 "
        "3) 给出多情景（牛市/震荡/熊市）下的差异化观点 4) 总结均衡结论。"
    )
