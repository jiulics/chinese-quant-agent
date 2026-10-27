"""辩论引擎的事件协议与回调类型定义。

事件类型：
- stage       阶段开始
- agent_start 某 Agent 开始
- agent_delta 流式增量
- agent_done  Agent 完成
- final       最终信号
- error       错误
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

# 回调函数签名：接收一个事件 dict，返回 awaitable
Callback = Callable[[dict[str, Any]], Awaitable[None]]


def stage_event(stage: str, message: str) -> dict[str, Any]:
    """构造阶段事件。"""
    return {"type": "stage", "stage": stage, "message": message}


def agent_start_event(role: str, label: str) -> dict[str, Any]:
    """构造 Agent 开始事件。"""
    return {"type": "agent_start", "role": role, "label": label}


def agent_delta_event(role: str, delta: str) -> dict[str, Any]:
    """构造流式增量事件。"""
    return {"type": "agent_delta", "role": role, "delta": delta}


def agent_done_event(role: str, content: str) -> dict[str, Any]:
    """构造 Agent 完成事件。"""
    return {"type": "agent_done", "role": role, "content": content}


def final_event(content: str) -> dict[str, Any]:
    """构造最终信号事件。"""
    return {"type": "final", "content": content}
