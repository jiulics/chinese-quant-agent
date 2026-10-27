"""LLM 客户端基础测试（不依赖真实服务）。"""
import pytest

from chinese_quant_agent.llm import LLMMessage


def test_message_to_dict():
    m = LLMMessage("user", "hello")
    assert m.to_dict() == {"role": "user", "content": "hello"}
