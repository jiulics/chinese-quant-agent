"""5 级深度配置：控制辩论的规模与详略。

深度 1（快速概览）→ 5（深度尽调）：
- agents: 参与角色列表
- rounds: 辩论轮次
- include_history: 是否使用历史K线
- include_multi_scenario: 是否多情景
- max_tokens_per_agent: 每个 Agent 的输出上限
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DepthConfig:
    level: int
    name: str
    agents: list[str]
    rounds: int
    include_history: bool
    include_multi_scenario: bool
    max_tokens_per_agent: int


def _c(level, name, agents, rounds, history, scenario, tokens):
    return DepthConfig(level, name, agents, rounds, history, scenario, tokens)


DEPTH_LEVELS: dict[int, DepthConfig] = {
    1: _c(1, "快速概览", ["analyst"], 0, False, False, 512),
    2: _c(2, "基础分析", ["analyst", "technical"], 0, True, False, 1024),
    3: _c(3, "标准研究", ["analyst", "technical", "risk"], 1, True, False, 1536),
    4: _c(4, "深度研究", ["analyst", "technical", "risk", "strategist"], 2, True, True, 2048),
    5: _c(5, "尽调级", ["analyst", "technical", "risk", "strategist", "moderator"], 3, True, True, 3072),
}


def get_depth_config(level: int) -> DepthConfig:
    """获取指定深度配置（1-5，越界自动钳制）。"""
    level = max(1, min(5, int(level)))
    return DEPTH_LEVELS[level]
