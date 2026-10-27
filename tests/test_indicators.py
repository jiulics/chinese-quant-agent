"""技术指标计算单元测试。"""
import pandas as pd
import pytest

from chinese_quant_agent.indicators import compute_indicators


def _make_df(n=100):
    import numpy as np
    close = np.linspace(10, 20, n)
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=n),
        "open": close - 0.1,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": np.full(n, 1000.0),
        "amount": np.full(n, 10000.0),
    })


def test_compute_indicators_returns_keys():
    df = _make_df()
    result = compute_indicators(df)
    for key in ["MA5", "MA10", "MA20", "MA60", "MACD", "KDJ_K", "RSI14"]:
        assert key in result


def test_ma_values_increasing():
    df = _make_df()
    result = compute_indicators(df)
    # 单调递增序列，短均线应大于长均线
    assert result["MA5"] > result["MA60"]
