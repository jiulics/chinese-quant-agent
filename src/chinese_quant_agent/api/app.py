"""FastAPI 应用工厂：组装中间件、数据源、编排器、记忆、技能与全部路由。

路由实现见 routes/ 目录，SSE 流式逻辑见 stream.py。
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings

from ..data import AutoProvider, MockProvider, TencentProvider
from ..llm import build_client_from_settings
from ..memory import MemoryStore
from ..skills import build_builtin_skills
from .routes.analyze import build_router as build_analyze_router
from .routes.stocks import build_router as build_stocks_router
from .routes.research import build_router as build_research_router
from .routes.assistant import build_router as build_assistant_router
from .routes.trading import build_router as build_trading_router


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    app = FastAPI(
        title="chinese-quant-agent",
        description="基于多智能体 LLM 的中文金融交易框架 API",
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 组装依赖：real_data 优先真实行情（BaoStock->AKShare->Mock 自动回退）
    real_data = AutoProvider()
    mock_data = MockProvider()
    tencent = TencentProvider()
    llm = build_client_from_settings(settings)
    memory = MemoryStore()
    skills = build_builtin_skills(real_data)

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "version": "0.3.0", "data_source": real_data.active_source}

    # 注册全部路由
    app.include_router(build_analyze_router(llm, real_data, mock_data))
    app.include_router(build_stocks_router(real_data, mock_data, tencent))
    app.include_router(build_research_router(llm, real_data, mock_data))
    app.include_router(build_assistant_router(llm, real_data, mock_data, memory))
    app.include_router(build_trading_router(real_data, mock_data, skills))

    return app


app = create_app()
