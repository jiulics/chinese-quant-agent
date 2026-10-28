"""腾讯实时行情数据源（盘中实时，纯 HTTP GET，无需 token）。

使用 qt.gtimg.cn 接口，返回指数与个股的盘中实时快照。
用于补充 BaoStock 日频数据的不足，提供分时级别的大盘/个股实时涨跌。

字段索引（以 ~ 分隔）：
  [1]名称 [2]代码 [3]现价 [4]昨收 [5]今开 [6]成交量(手) [31]涨跌额 [32]涨跌幅%
  [33]最高 [34]最低 [37]成交额(万) [30]时间戳
"""
from __future__ import annotations

import asyncio
import logging
import urllib.request

from .provider import DataProvider

logger = logging.getLogger(__name__)

# 腾讯代码 -> (本地符号, 中文名)
_TENCENT_INDICES: dict[str, tuple[str, str]] = {
    "sh000001": ("000001", "上证指数"),
    "sz399001": ("399001", "深证成指"),
    "sz399006": ("399006", "创业板指"),
    "sh000300": ("000300", "沪深300"),
    "sh000016": ("000016", "上证50"),
    "sz399905": ("399905", "中证500"),
    "sh000688": ("000688", "科创50"),
}


def _to_tencent_code(symbol: str) -> str:
    """将纯数字代码转为腾讯代码（自动判断沪/深）。"""
    s = symbol.strip().lower().replace("sh", "").replace("sz", "").replace(".", "")
    if s.startswith(("6", "9", "5", "000")):
        return "sh" + s
    return "sz" + s


class TencentProvider:
    """腾讯实时行情数据源（指数 + 个股盘中快照）。"""

    name = "tencent"

    def _fetch_raw(self, codes: list[str]) -> str:
        """拉取原始返回（GBK 编码）。"""
        url = "https://qt.gtimg.cn/q=" + ",".join(codes)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("gbk", errors="replace")

    @staticmethod
    def _parse_line(line: str) -> dict | None:
        """解析单行 v_xxx="..." 返回快照字典。"""
        if "=" not in line:
            return None
        _, val = line.split("=", 1)
        val = val.strip().rstrip(";")
        if val.startswith('"'):
            val = val[1:-1]
        f = val.split("~")
        if len(f) < 38:
            return None

        def num(x, nd=None):
            try:
                v = float(x)
                return round(v, nd) if nd is not None else v
            except (TypeError, ValueError):
                return None

        return {
            "name": f[1],
            "symbol": f[2],
            "price": num(f[3]),
            "preclose": num(f[4]),
            "open": num(f[5]),
            "change": num(f[31]),
            "change_pct": num(f[32]),
            "high": num(f[33]),
            "low": num(f[34]),
            "volume": num(f[6]),        # 手
            "amount": num(f[37]),        # 万元
            "timestamp": f[30],
        }

    async def get_realtime_indices(self) -> list[dict]:
        """获取大盘指数盘中实时快照。"""
        def _fetch():
            raw = self._fetch_raw(list(_TENCENT_INDICES.keys()))
            results = []
            for line in raw.strip().split("\n"):
                d = self._parse_line(line)
                if d:
                    results.append(d)
            return results

        return await asyncio.to_thread(_fetch)

    async def get_realtime_quote(self, symbol: str) -> dict | None:
        """获取单只股票盘中实时快照。"""
        def _fetch():
            code = _to_tencent_code(symbol)
            raw = self._fetch_raw([code])
            for line in raw.strip().split("\n"):
                d = self._parse_line(line)
                if d:
                    return d
            return None

        return await asyncio.to_thread(_fetch)
