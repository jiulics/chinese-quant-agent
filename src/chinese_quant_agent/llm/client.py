"""LLM 客户端：基于 OpenAI 兼容协议的异步客户端。

设计目标：
- 一个客户端接入任意 OpenAI 兼容服务（DeepSeek / Qwen / vLLM / Ollama / LM Studio）。
- 每个开发者只需在 .env 中配置 base_url / api_key / model 即可自定义自己的模型。
- 纯本地运行：指向本地服务地址即可，无需联网、无需外部 API Key。
"""
from __future__ import annotations

import logging

from openai import AsyncOpenAI

from .models import LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


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
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    def _build_payload(
        self,
        messages: list[LLMMessage],
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> list[dict[str, str]]:
        payload: list[dict[str, str]] = []
        if system:
            payload.append({"role": "system", "content": system})
        payload.extend(m.to_dict() for m in messages)
        return payload

    def _gen_kwargs(self, temperature: float | None, max_tokens: int | None) -> dict:
        return {
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
        }

    async def chat(
        self,
        messages: list[LLMMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """发送对话并返回助手回复。"""
        resp = await self._client.chat.completions.create(
            model=self.model,
            messages=self._build_payload(messages, system, temperature, max_tokens),
            **self._gen_kwargs(temperature, max_tokens),
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

    async def stream_chat(
        self,
        messages: list[LLMMessage],
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """流式对话：异步生成器，逐段 yield 文本增量。"""
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=self._build_payload(messages, system, temperature, max_tokens),
            **self._gen_kwargs(temperature, max_tokens),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
