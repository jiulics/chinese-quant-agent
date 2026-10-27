"""示例：分析单只股票并打印完整结果。"""
import asyncio

from chinese_quant_agent.main import analyze_stock


async def main():
    result = await analyze_stock("600519")
    print("=" * 60)
    print(f"股票：{result['quote'].name}（{result['quote'].symbol}）")
    print(f"最新价：{result['quote'].price}")
    print("\n【技术指标】")
    for k, v in result["indicators"].items():
        print(f"  {k}: {v}")
    print("\n【最终投资信号】")
    print(result["final_signal"])
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
