"""BaoStock 真实数据源：国内免费、无需 token 的 A 股行情接口。

BaoStock 提供日/周/月 K 线、复权数据、估值指标（PE/PB）等，
是解决"真实行情"的首选免费数据源。同步接口放在线程中执行。
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd

from .provider import DataProvider, StockHistory, StockQuote

logger = logging.getLogger(__name__)

# 常见股票名称（BaoStock 列表查询失败时的兜底）
_NAME_FALLBACK = {
    "600519": "贵州茅台", "000001": "平安银行", "300750": "宁德时代",
    "601318": "中国平安", "600036": "招商银行", "000858": "五粮液",
    "601899": "紫金矿业", "600900": "长江电力", "600000": "浦发银行",
    "000002": "万科A", "002594": "比亚迪", "601012": "隆基绿能",
}


def _to_bs_code(symbol: str) -> str:
    """6 位代码 -> BaoStock 格式（sh./sz.）。"""
    symbol = symbol.strip()
    if symbol.startswith(("sh.", "sz.")):
        return symbol
    prefix = "sh" if symbol.startswith(("6", "9", "5")) else "sz"
    return f"{prefix}.{symbol}"


class BaostockProvider(DataProvider):
    """基于 BaoStock 的真实 A 股数据源。"""

    def __init__(self) -> None:
        self._bs = None
        self._available = False
        self._stock_list_cache: pd.DataFrame | None = None
        try:
            import baostock as bs
            self._bs = bs
            self._available = True
        except ImportError:
            logger.warning("baostock 未安装，BaostockProvider 不可用")

    @property
    def available(self) -> bool:
        return self._available

    def _login(self):
        if not self._available:
            raise RuntimeError("baostock 未安装")
        import time
        last_err = None
        for attempt in range(3):
            try:
                lg = self._bs.login()
                if lg.error_code == "0":
                    return
                last_err = lg.error_msg
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
            time.sleep(1.0 * (attempt + 1))
        raise RuntimeError(f"BaoStock 登录失败: {last_err}")

    def _logout(self):
        if self._available:
            self._bs.logout()

    async def get_quote(self, symbol: str) -> StockQuote:
        """获取最新行情（取最近一交易日 K 线作为快照）。"""
        def _fetch():
            self._login()
            try:
                bs_code = _to_bs_code(symbol)
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
                rs = self._bs.query_history_k_data_plus(
                    bs_code,
                    "date,code,open,high,low,close,preclose,volume,amount,pctChg,turn,tradestatus",
                    start_date=start, end_date=end, frequency="d", adjustflag="3",
                )
                if rs.error_code != "0":
                    raise RuntimeError(f"查询失败: {rs.error_msg}")
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    raise RuntimeError(f"{symbol} 无行情数据")
                # 取最后一个交易日（tradestatus=1）
                trade_rows = [r for r in rows if r[11] == "1"]
                row = trade_rows[-1] if trade_rows else rows[-1]
                price = float(row[5])
                preclose = float(row[6]) if row[6] else price
                pct = float(row[9]) if row[9] else 0.0
                return StockQuote(
                    symbol=symbol,
                    name=_NAME_FALLBACK.get(symbol, f"股票{symbol}"),
                    price=round(price, 2),
                    change=round(price - preclose, 2),
                    change_pct=round(pct, 2),
                    open=round(float(row[2]), 2),
                    high=round(float(row[3]), 2),
                    low=round(float(row[4]), 2),
                    volume=float(row[7]),
                    amount=float(row[8]),
                    timestamp=row[0],
                )
            finally:
                self._logout()

        return await asyncio.to_thread(_fetch)


    async def get_valuation_data(self, symbol: str) -> dict:
        """获取最新估值指标（PE-TTM / PB / PS / PCF）。"""
        def _fetch():
            self._login()
            try:
                bs_code = _to_bs_code(symbol)
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
                rs = self._bs.query_history_k_data_plus(
                    bs_code, "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                    start_date=start, end_date=end, frequency="d", adjustflag="3",
                )
                if rs.error_code != "0":
                    return {}
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                if not rows:
                    return {}
                row = rows[-1]

                def f(x):
                    try:
                        return float(x)
                    except (TypeError, ValueError):
                        return None

                return {
                    "date": row[0],
                    "close": f(row[2]),
                    "pe_ttm": f(row[3]),
                    "pb_mrq": f(row[4]),
                    "ps_ttm": f(row[5]),
                    "pcf_ttm": f(row[6]),
                }
            finally:
                self._logout()

        return await asyncio.to_thread(_fetch)

    async def get_financial_data(self, symbol: str) -> dict:
        """获取最新财务数据（盈利能力/成长/偿债），合并为单一字典。"""
        def _fetch():
            self._login()
            try:
                bs_code = _to_bs_code(symbol)
                result: dict = {}

                def f(x):
                    try:
                        return float(x)
                    except (TypeError, ValueError):
                        return None

                # 盈利能力
                rs = self._bs.query_profit_data(code=bs_code, year=2025, quarter=3)
                if rs.error_code == "0":
                    rows = []
                    while rs.next():
                        rows.append(rs.get_row_data())
                    if rows:
                        r = rows[-1]
                        profit_fields = ["roeAvg", "npMargin", "gpMargin", "netProfit", "epsTTM", "MBRevenue", "totalShare", "liqaShare"]
                        if hasattr(rs, "fields"):
                            for k, v in zip(rs.fields, r):
                                if k in profit_fields:
                                    result[k] = f(v)
                        else:
                            result["roeAvg"] = f(r[3]); result["npMargin"] = f(r[4])
                            result["gpMargin"] = f(r[5]); result["netProfit"] = f(r[6])
                            result["epsTTM"] = f(r[7]); result["MBRevenue"] = f(r[8])

                # 成长能力
                rs = self._bs.query_growth_data(code=bs_code, year=2025, quarter=3)
                if rs.error_code == "0":
                    rows = []
                    while rs.next():
                        rows.append(rs.get_row_data())
                    if rows:
                        r = rows[-1]
                        growth_fields = ["YOYEquity", "YOYAsset", "YOYNI", "YOYEPSBasic", "YOYPNI"]
                        if hasattr(rs, "fields"):
                            for k, v in zip(rs.fields, r):
                                if k in growth_fields:
                                    result[k] = f(v)
                        else:
                            result["YOYNI"] = f(r[3]); result["YOYEPSBasic"] = f(r[4]); result["YOYPNI"] = f(r[5])

                # 偿债能力
                rs = self._bs.query_balance_data(code=bs_code, year=2025, quarter=3)
                if rs.error_code == "0":
                    rows = []
                    while rs.next():
                        rows.append(rs.get_row_data())
                    if rows:
                        r = rows[-1]
                        balance_fields = ["currentRatio", "quickRatio", "cashRatio", "liabilityToAsset", "assetToEquity"]
                        if hasattr(rs, "fields"):
                            for k, v in zip(rs.fields, r):
                                if k in balance_fields:
                                    result[k] = f(v)
                        else:
                            result["currentRatio"] = f(r[3]); result["quickRatio"] = f(r[4])
                            result["liabilityToAsset"] = f(r[6])

                return result
            finally:
                self._logout()

        return await asyncio.to_thread(_fetch)

    async def get_history(
        self,
        symbol: str,
        *,
        start: str | None = None,
        end: str | None = None,
        period: str = "daily",
    ) -> StockHistory:
        freq_map = {"daily": "d", "weekly": "w", "monthly": "m"}
        freq = freq_map.get(period, "d")
        if not start:
            start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")

        def _fetch():
            self._login()
            try:
                bs_code = _to_bs_code(symbol)
                if freq == "d":
                    fields = "date,code,open,high,low,close,preclose,volume,amount,pctChg,turn,tradestatus"
                else:
                    fields = "date,code,open,high,low,close,volume,amount,pctChg"
                rs = self._bs.query_history_k_data_plus(
                    bs_code, fields, start_date=start, end_date=end,
                    frequency=freq, adjustflag="2",
                )
                if rs.error_code != "0":
                    raise RuntimeError(f"查询失败: {rs.error_msg}")
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                df = pd.DataFrame(rows, columns=rs.fields)
                for col in ("open", "high", "low", "close", "preclose", "volume", "amount", "pctChg"):
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                return StockHistory(symbol=symbol, df=df)
            finally:
                self._logout()

        return await asyncio.to_thread(_fetch)

    async def get_stock_list(self) -> pd.DataFrame:
        if self._stock_list_cache is not None:
            return self._stock_list_cache

        def _fetch():
            self._login()
            try:
                rs = self._bs.query_stock_basic()
                if rs.error_code != "0":
                    raise RuntimeError(f"查询失败: {rs.error_msg}")
                rows = []
                while rs.next():
                    rows.append(rs.get_row_data())
                df = pd.DataFrame(rows, columns=rs.fields)
                # code, code_name, ipoDate, outDate, type, status
                df = df[(df["type"] == "1") & (df["status"] == "1")]
                df["代码"] = df["code"].str.replace("sh.", "").str.replace("sz.", "")
                df["名称"] = df["code_name"]
                result = df[["代码", "名称"]]
                self._stock_list_cache = result
                return result
            finally:
                self._logout()

        return await asyncio.to_thread(_fetch)

    async def search_stocks(self, query: str, limit: int = 20) -> list[dict[str, str]]:
        q = query.strip()
        try:
            df = await self.get_stock_list()
        except Exception:  # noqa: BLE001
            df = pd.DataFrame([{"代码": k, "名称": v} for k, v in _NAME_FALLBACK.items()])
        mask = df["代码"].str.contains(q, na=False) | df["名称"].str.contains(q, na=False)
        result = df[mask].head(limit)
        return [{"symbol": r["代码"], "name": r["名称"]} for _, r in result.iterrows()]
