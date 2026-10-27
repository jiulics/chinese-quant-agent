"""Agent 角色注册表：角色名 -> Agent 类。"""
from __future__ import annotations

from ..agents import AnalystAgent, RiskAgent, StrategistAgent, TechnicalAgent

AGENT_CLASSES: dict[str, type] = {
    "analyst": AnalystAgent,
    "technical": TechnicalAgent,
    "risk": RiskAgent,
    "strategist": StrategistAgent,
}
