"""模拟交易与 Skill 中心路由。"""
from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ...data import DataProvider
from ...trading import PaperTradingEngine
from ...skills import SkillManager

logger = logging.getLogger(__name__)


class OrderRequest(BaseModel):
    symbol: str
    quantity: int


class SkillRunRequest(BaseModel):
    kwargs: dict = {}


def build_router(data: DataProvider, mock_data: DataProvider, skills: SkillManager) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["trading"])
    engine = PaperTradingEngine(mock_data)

    @router.get("/trading/snapshot")
    async def snapshot():
        return await engine.snapshot()

    @router.post("/trading/buy")
    async def buy(req: OrderRequest):
        try:
            return await engine.buy(req.symbol, req.quantity)
        except ValueError as e:
            return {"error": str(e)}

    @router.post("/trading/sell")
    async def sell(req: OrderRequest):
        try:
            return await engine.sell(req.symbol, req.quantity)
        except ValueError as e:
            return {"error": str(e)}

    @router.get("/trading/orders")
    async def orders(limit: int = 50):
        return await engine.orders(limit)

    @router.get("/skills")
    async def list_skills():
        return skills.list()

    @router.post("/skills/{name}/run")
    async def run_skill(name: str, req: SkillRunRequest):
        kw = req.kwargs or {}
        return {"result": await skills.run(name, **kw)}

    return router
