"""多智能体：不同角色的分析 Agent。"""

from .base import Agent, AgentResult
from .analyst import AnalystAgent
from .technical import TechnicalAgent
from .risk import RiskAgent
from .strategist import StrategistAgent

__all__ = [
    "Agent",
    "AgentResult",
    "AnalystAgent",
    "TechnicalAgent",
    "RiskAgent",
    "StrategistAgent",
]
