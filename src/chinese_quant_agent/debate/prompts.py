"""各角色 Agent 的输入 prompt 构造。

核心原则：先由编排器拉取全量真实数据（行情/历史/指标/估值/财务），
再在这里按角色裁剪出「贴切且完整」的数据视图，确保每个 Agent 都基于
同一份真实数据推理，不靠记忆脑补数字。
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


def _fmt_pct(v: Any, nd: int = 2) -> str:
    """格式化百分比（财务数据多为小数，如 0.2637 -> 26.37%）。"""
    if v is None:
        return "-"
    try:
        f = float(v)
        if math.isnan(f):
            return "-"
        # 绝对值 <= 2 视为小数比例，转百分比
        if abs(f) <= 2:
            return f"{f * 100:.{nd}f}%"
        return f"{f:.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


def _fmt_quote(quote: Any) -> str:
    """格式化行情快照为简洁可读文本。"""
    if quote is None:
        return "（无实时行情）"
    if hasattr(quote, "price"):
        return (
            f"{getattr(quote, 'name', '')}（{getattr(quote, 'symbol', '')}）"
            f"最新价 {_fmt_num(getattr(quote, 'price', None))} 元，"
            f"涨跌 {_fmt_num(getattr(quote, 'change', None))}"
            f"（{_fmt_num(getattr(quote, 'change_pct', None))}%），"
            f"今开 {_fmt_num(getattr(quote, 'open', None))}，"
            f"最高 {_fmt_num(getattr(quote, 'high', None))}，"
            f"最低 {_fmt_num(getattr(quote, 'low', None))}，"
            f"成交量 {_fmt_num(getattr(quote, 'volume', None), 0)} 手，"
            f"成交额 {_fmt_num(getattr(quote, 'amount', None), 0)} 元"
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


def _fmt_valuation(v: dict) -> str:
    """格式化估值指标。"""
    if not v:
        return "（无估值数据）"
    return (
        f"PE-TTM {_fmt_num(v.get('pe_ttm'))} 倍，"
        f"PB {_fmt_num(v.get('pb_mrq'))} 倍，"
        f"PS-TTM {_fmt_num(v.get('ps_ttm'))} 倍，"
        f"PCF {_fmt_num(v.get('pcf_ttm'))} 倍"
    )


def _fmt_financials(f: dict) -> str:
    """格式化财务数据（盈利/成长/偿债）。"""
    if not f:
        return "（无财务数据）"
    lines = []
    # 盈利能力
    profit = []
    if f.get("roeAvg") is not None:
        profit.append(f"ROE {_fmt_pct(f['roeAvg'])}")
    if f.get("gpMargin") is not None:
        profit.append(f"毛利率 {_fmt_pct(f['gpMargin'])}")
    if f.get("npMargin") is not None:
        profit.append(f"净利率 {_fmt_pct(f['npMargin'])}")
    if f.get("epsTTM") is not None:
        profit.append(f"EPS(TTM) {_fmt_num(f['epsTTM'])} 元")
    if f.get("MBRevenue") is not None:
        profit.append(f"主营收入 {_fmt_num(f['MBRevenue'] / 1e8, 2)} 亿元")
    if f.get("netProfit") is not None:
        profit.append(f"净利润 {_fmt_num(f['netProfit'] / 1e8, 2)} 亿元")
    if profit:
        lines.append("盈利能力：" + "，".join(profit))

    # 成长能力
    growth = []
    if f.get("YOYNI") is not None:
        growth.append(f"净利润同比 {_fmt_pct(f['YOYNI'])}")
    if f.get("YOYEPSBasic") is not None:
        growth.append(f"EPS同比 {_fmt_pct(f['YOYEPSBasic'])}")
    if f.get("YOYEquity") is not None:
        growth.append(f"净资产同比 {_fmt_pct(f['YOYEquity'])}")
    if growth:
        lines.append("成长能力：" + "，".join(growth))

    # 偿债能力
    debt = []
    if f.get("currentRatio") is not None:
        debt.append(f"流动比率 {_fmt_num(f['currentRatio'])}")
    if f.get("quickRatio") is not None:
        debt.append(f"速动比率 {_fmt_num(f['quickRatio'])}")
    if f.get("liabilityToAsset") is not None:
        debt.append(f"资产负债率 {_fmt_pct(f['liabilityToAsset'])}")
    if debt:
        lines.append("偿债能力：" + "，".join(debt))

    return "\n".join(lines) if lines else "（财务数据为空）"


def build_prompt(role: str, context: dict) -> str:
    """根据角色名构造输入 prompt（裁剪出该角色需要的完整数据视图）。"""
    symbol = context.get("symbol", "未知")
    quote = _fmt_quote(context.get("quote"))
    indicators = _fmt_indicators(context.get("indicators", {}))
    valuation = _fmt_valuation(context.get("valuation", {}))
    financials = _fmt_financials(context.get("financials", {}))

    if role == "基本面分析师":
        return (
            f"请对股票 {symbol} 做基本面分析。\n\n"
            f"【实时行情】{quote}\n"
            f"【估值指标】{valuation}\n"
            f"【财务数据】\n{financials}\n\n"
            "请严格基于以上真实数据输出：1) 基本面概览 2) 估值判断（引用上面的 PE/PB/ROE）"
            "3) 成长性与盈利质量 4) 主要风险。不要臆造数据。"
        )
    if role == "技术面分析师":
        return (
            f"请对股票 {symbol} 做技术面分析。\n\n"
            f"【技术指标】{indicators}\n"
            f"【实时行情】{quote}\n\n"
            "请基于以上真实指标输出：1) 趋势判断 2) 关键支撑/阻力位 3) 技术信号。"
        )
    if role == "风控分析师":
        return (
            f"请对股票 {symbol} 做风险评估。\n\n"
            f"【实时行情】{quote}\n"
            f"【估值指标】{valuation}\n"
            f"【偿债能力】{financials}\n\n"
            "请输出：1) 风险等级 2) 建议仓位 3) 止损位 4) 风险提示。"
        )
    if role == "策略师":
        return _build_summary_prompt(symbol, context)
    if role == "辩论主持人":
        return _build_moderator_prompt(symbol, context)
    if role == "情景分析师":
        return (
            f"请对股票 {symbol} 做多情景分析。\n\n"
            f"【当前行情】{quote}\n"
            f"【估值指标】{valuation}\n\n"
            "请分别输出【牛市情景】【震荡情景】【熊市情景】下的观点，"
            "每种情景说明：触发条件、核心逻辑、操作建议。"
        )
    return f"请分析股票 {symbol}。"


def _build_summary_prompt(symbol: str, context: dict) -> str:
    analyses = context.get("analyses", [])
    quote = _fmt_quote(context.get("quote"))
    valuation = _fmt_valuation(context.get("valuation", {}))
    summary = "\n\n".join(f"[{a.role}]\n{a.content}" for a in analyses)
    return (
        f"请综合以下对股票 {symbol} 的分析，给出最终投资信号。\n\n"
        f"【基准数据】{quote}；{valuation}\n\n"
        f"【各分析师观点】\n{summary}\n\n"
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
