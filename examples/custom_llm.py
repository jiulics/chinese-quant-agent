"""示例：自定义 LLM 客户端（演示模型可替换性）。

展示如何直接构造 LLMClient 指向任意 OpenAI 兼容服务，
而无需依赖 .env 配置。
"""
import asyncio

from chinese_quant_agent.llm import LLMClient, LLMMessage


async def main():
    # 换成你自己的模型服务地址
    client = LLMClient(
        base_url="http://localhost:11434/v1",  # Ollama
        api_key="ollama",
        model="qwen2.5:7b",
    )
    resp = await client.complete(
        "用一句话介绍 A 股市场的特点。",
        system="你是中文金融助手。",
    )
    print(resp.content)


if __name__ == "__main__":
    asyncio.run(main())
