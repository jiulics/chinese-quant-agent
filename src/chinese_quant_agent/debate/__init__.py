"""辩论机制：多智能体辩论式分析（5 级深度 + 多情景）。"""

from .debate import DebateEngine
from .depth import DEPTH_LEVELS, get_depth_config
from .moderator import ModeratorAgent, MultiScenarioAgent

__all__ = [
    "DEPTH_LEVELS",
    "get_depth_config",
    "DebateEngine",
    "ModeratorAgent",
    "MultiScenarioAgent",
]
