"""Agent 基类。

每个 Agent 封装一个角色（分析师/技术面/风控/策略），
通过共享的 LLMClient 与数据源协同工作。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..llm import LLMClient


@dataclass
class AgentResult:
    """Agent 输出结果。"""

    role: str                 # 角色名
    content: str              # 分析文本
    meta: dict = field(default_factory=dict)  # 附加结构化信息


class Agent(ABC):
    """多智能体基类。"""

    role: str = "agent"

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    @property
    def system_prompt(self) -> str:
        """该角色的系统提示词。"""
        return "你是一名专业的金融分析助手。"

    @abstractmethod
    async def run(self, context: dict) -> AgentResult:
        """根据上下文执行分析，返回结果。

        context 中通常包含：symbol、quote、history、market 等。
        """
