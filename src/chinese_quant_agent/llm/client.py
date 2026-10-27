"""LLM 客户端：基于 OpenAI 兼容协议。

设计目标：
- 一个客户端接入任意 OpenAI 兼容服务（DeepSeek / Qwen / vLLM / Ollama / LM Studio）。
- 每个开发者只需在 .env 中配置 base_url / api_key / model 即可自定义自己的模型。
- 纯本地运行：指向本地服务地址即可，无需联网、无需外部 API Key。
"""
from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMMessage:
    """一条对话消息。"""

    __slots__ = ("role", "content")

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMResponse:
    """模型返回结果。"""

    __slots__ = ("content", "raw")

    def __init__(self, content: str, raw: Any = None) -> None:
        self.content = content
        self.raw = raw


class LLMClient:
    """OpenAI 兼容的异步 LLM 客户端。

    参数：
        base_url: 服务地址（OpenAI 兼容接口根路径，含 /v1）。
        api_key: API Key；本地模型可传任意占位值。
        model: 模型名称。
        temperature / max_tokens / timeout: 生成与超时参数。
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

    async def chat(
        self,
        messages: list[LLMMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """发送对话并返回助手回复。

        messages 为对话历史；system 会作为 system 消息置于最前。
        """
        payload: list[dict[str, str]] = []
        if system:
            payload.append({"role": "system", "content": system})
        payload.extend(m.to_dict() for m in messages)

        resp = await self._client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=self.max_tokens if max_tokens is None else max_tokens,
        )
        content = resp.choices[0].message.content or ""
        logger.debug("LLM 回复长度=%d", len(content))
        return LLMResponse(content=content, raw=resp)

    async def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """单轮补全：传入一条 user 消息。"""
        return await self.chat(
            [LLMMessage("user", prompt)],
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )


def build_client_from_settings(settings: Any) -> LLMClient:
    """从 Settings 对象构建 LLMClient，便于依赖注入。"""
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout,
    )
