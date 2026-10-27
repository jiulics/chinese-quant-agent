"""智能助手：联网搜索 + 工具调用 + 事实记忆的对话编排。

流程：
1. 载入会话历史与相关记忆
2. LLM 决定是否调用工具（function calling）
3. 执行工具，将结果回填
4. 生成最终回答并沉淀事实
"""
from __future__ import annotations

import json
import logging
from typing import Any

from ..llm import LLMClient, LLMMessage
from ..memory import MemoryStore
from ..tools import Registry

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 5


class AssistantAgent:
    """带工具调用的智能助手。"""

    SYSTEM = (
        "你是一名中文金融智能助手，可以联网搜索、调用数据工具、并利用 AI 记忆。"
        "回答应客观、专业、简洁，涉及投资建议时务必附免责声明："
        "内容仅供参考，不构成投资建议。"
    )

    def __init__(
        self,
        llm: LLMClient,
        tools: Registry,
        memory: MemoryStore | None = None,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.memory = memory

    async def chat(
        self,
        user_message: str,
        conv_id: str = "default",
        callback=None,
    ) -> dict:
        """处理一条用户消息，返回 {answer, tool_calls, facts}。"""
        await self._emit(callback, {"type": "assistant_start"})

        # 载入历史与相关记忆
        history = await self.memory.get_conversation(conv_id) if self.memory else []
        facts = await self.memory.list_facts(user_message[:20], limit=5) if self.memory else []

        messages: list[LLMMessage] = []
        if facts:
            fact_text = "\n".join(f"- {f['content']}" for f in facts)
            messages.append(LLMMessage("user", f"[相关记忆]\n{fact_text}"))
        messages.extend(LLMMessage(m["role"], m["content"]) for m in history)
        messages.append(LLMMessage("user", user_message))

        tool_calls_log: list[dict] = []

        for _round in range(MAX_TOOL_ROUNDS):
            resp = await self.llm._client.chat.completions.create(
                model=self.llm.model,
                messages=[{"role": "system", "content": self.SYSTEM}]
                         + [m.to_dict() for m in messages],
                tools=self.tools.to_openai(),
                temperature=self.llm.temperature,
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                # 无工具调用，生成最终回答
                answer = msg.content or ""
                break

            # 执行工具调用
            messages.append(LLMMessage("assistant", msg.content or ""))
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                await self._emit(callback, {"type": "tool_call", "name": name, "args": args})
                result = await self.tools.execute(name, args)
                tool_calls_log.append({"name": name, "args": args, "result": result})
                messages.append(LLMMessage(
                    "tool",
                    json.dumps({"tool": name, "result": result}, ensure_ascii=False),
                ))
        else:
            answer = "抱歉，工具调用轮次过多，请简化问题后重试。"

        # 沉淀事实（异步，不阻塞回答）
        if self.memory:
            await self.memory.append_message(conv_id, "user", user_message)
            await self.memory.append_message(conv_id, "assistant", answer)

        await self._emit(callback, {"type": "assistant_done", "answer": answer})
        return {
            "answer": answer,
            "tool_calls": tool_calls_log,
            "facts": facts,
        }

    async def _emit(self, callback, event: dict) -> None:
        if callback:
            await callback(event)
