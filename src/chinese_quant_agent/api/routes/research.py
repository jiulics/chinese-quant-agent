"""通用研究、股票筛选、选股助手路由。"""
from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ...data import DataProvider
from ...llm import LLMClient
from ...research import GeneralResearcher
from ...screener import Screener
from ...picker import StockPicker

logger = logging.getLogger(__name__)


class GeneralRequest(BaseModel):
    topic: str


class ScreenRequest(BaseModel):
    query: str | None = None
    criteria: dict | None = None


class PickRequest(BaseModel):
    need: str


def build_router(llm: LLMClient, data: DataProvider, mock_data: DataProvider) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["research"])
    researcher = GeneralResearcher(llm)
    screener = Screener(mock_data, llm)
    picker = StockPicker(screener, llm)

    @router.post("/research/general")
    async def general_research(req: GeneralRequest):
        return await researcher.research(req.topic)

    @router.post("/screener")
    async def screen(req: ScreenRequest):
        if req.query:
            return await screener.natural_screen(req.query)
        return await screener.screen(req.criteria or {})

    @router.post("/picker")
    async def pick(req: PickRequest):
        return await picker.pick(req.need)

    return router
