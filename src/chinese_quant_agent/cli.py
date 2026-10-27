"""命令行入口：cqa analyze 600519 / cqa serve"""
from __future__ import annotations

import asyncio
import logging

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel

from .main import analyze_stock
from config.settings import get_settings

app = typer.Typer(name="cqa", help="chinese-quant-agent 中文金融多智能体交易框架")
console = Console()


@app.command()
def analyze(symbol: str = typer.Argument(..., help="股票代码，如 600519")):
    """对单只 A 股执行多智能体分析。"""
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    console.print(f"[bold cyan]正在分析 {symbol} ...[/bold cyan]")
    result = asyncio.run(analyze_stock(symbol))

    q = result["quote"]
    console.print(Panel(
        f"股票：{q.name}（{q.symbol}）\n"
        f"最新价：{q.price}  涨跌幅：{q.change_pct}%\n\n"
        f"技术指标：{result['indicators']}",
        title="行情概览",
    ))

    for i, a in enumerate(result["analyses"], 1):
        console.print(Panel(a, title=f"分析 {i}"))

    console.print(Panel(result["final_signal"], title="最终投资信号", border_style="green"))


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="监听地址"),
    port: int = typer.Option(8000, help="监听端口"),
    reload: bool = typer.Option(False, help="开发模式热重载"),
):
    """启动 FastAPI Web 服务。"""
    console.print(f"[bold green]启动服务: http://localhost:{port} [/bold green]")
    uvicorn.run(
        "chinese_quant_agent.api.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def version():
    """显示版本。"""
    from . import __version__
    console.print(f"chinese-quant-agent v{__version__}")


if __name__ == "__main__":
    app()
