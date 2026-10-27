"""常用技术指标计算（基于 pandas）。

返回一个字典，键为指标名，值为最新值或小序列，供技术面 Agent 使用。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _sma(series: pd.Series, n: int) -> pd.Series:
    return series.rolling(window=n, min_periods=n).mean()


def _ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n, adjust=False).mean()


def _rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_indicators(df: pd.DataFrame) -> dict:
    """计算指标并返回最新值与近端概览。

    df 需含列 close / high / low / volume。
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    ma5 = _sma(close, 5)
    ma10 = _sma(close, 10)
    ma20 = _sma(close, 20)
    ma60 = _sma(close, 60)

    # MACD
    ema12 = _ema(close, 12)
    ema26 = _ema(close, 26)
    dif = ema12 - ema26
    dea = _ema(dif, 9)
    macd = (dif - dea) * 2

    # KDJ
    low_n = low.rolling(window=9, min_periods=9).min()
    high_n = high.rolling(window=9, min_periods=9).max()
    rsv = (close - low_n) / (high_n - low_n).replace(0, np.nan) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d

    rsi14 = _rsi(close, 14)

    def _last(s: pd.Series) -> float:
        v = s.dropna()
        return round(float(v.iloc[-1]), 3) if not v.empty else float("nan")

    return {
        "最新收盘价": _last(close),
        "MA5": _last(ma5),
        "MA10": _last(ma10),
        "MA20": _last(ma20),
        "MA60": _last(ma60),
        "MACD_DIF": _last(dif),
        "MACD_DEA": _last(dea),
        "MACD": _last(macd),
        "KDJ_K": _last(k),
        "KDJ_D": _last(d),
        "KDJ_J": _last(j),
        "RSI14": _last(rsi14),
        "近5日收盘": [round(float(x), 2) for x in close.tail(5)],
    }
