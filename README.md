# chinese-quant-agent

> 基于多智能体 LLM 的中文金融交易框架

一个用 Python 后端 + Vue 3 前端构建的开源框架，面向 A 股：从股票接口拉取行情，交给多个专业化 LLM Agent 协作分析，输出结构化的**中文投资信号**，并覆盖研究、筛选、选股、智能助手、模拟交易等完整投研闭环。

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 **单股研究** | 多智能体辩论式分析（5 级深度）、多情景观点呈现 |
| 🌐 **通用研究** | 自然语言提问，研究任意市场主题 |
| 🧮 **股票筛选** | 自然语言 + 条件筛选，从 6000+ 只 A 股发现标的 |
| 🎯 **选股助手** | 按研究需求描述匹配候选股票池 |
| 🤖 **智能助手** | 联网搜索 + 工具调用 + 事实记忆 |
| 🧠 **AI 记忆** | 项目级记忆与事实沉淀 |
| 🧩 **Skill 中心** | 创建和管理自定义数据获取技能 |
| 📊 **模拟交易** | 纸面交易与复盘 |

## 🏗️ 技术栈

- **后端**：Python 3.11+ · FastAPI · 多智能体编排 · OpenAI 兼容 LLM · akshare
- **前端**：Vue 3 · TypeScript · Vite · Element Plus · ECharts · Pinia
- **模型**：任意 OpenAI 兼容服务（DeepSeek / Qwen / vLLM / Ollama / LM Studio），**可纯本地运行**

## 🚀 快速开始

### 1. 后端

```bash
# 要求 Python 3.11+，推荐 uv
git clone https://github.com/<your-name>/chinese-quant-agent.git
cd chinese-quant-agent
uv sync          # 或 pip install -e ".[dev]"
cp .env.example .env   # 配置你的模型
```

### 2. 前端

```bash
cd web
npm install
npm run dev      # 开发服务器，默认 http://localhost:5173
```

### 3. 运行后端服务

```bash
# 启动 FastAPI 服务（默认 http://localhost:8000）
cqa serve
```

## 📁 目录结构

```
src/chinese_quant_agent/
├── agents/          # 多智能体（分析师/技术/风控/策略/辩论）
├── data/            # 数据层（抽象 + akshare + 自定义 Skill）
├── llm/             # LLM 接入（OpenAI 兼容）
├── indicators/      # 技术指标
├── memory/          # AI 记忆（项目级 + 事实沉淀）
├── tools/           # 工具调用 + 联网搜索
├── trading/         # 模拟交易引擎
├── api/             # FastAPI Web 服务
├── orchestrator.py  # 编排器
└── cli.py           # 命令行入口

web/                 # Vue 3 前端
└── src/
    ├── views/       # 各功能模块视图
    ├── api/         # 后端 API 客户端
    ├── stores/      # Pinia 状态管理
    └── components/  # 通用组件
```

## 📖 文档

- [产品需求规格 (PRD)](docs/PRD.md)
- [技术架构设计](docs/ARCHITECTURE.md)

## ⚠️ 免责声明

本项目仅供学习与研究使用，所有分析结果**不构成任何投资建议**。股市有风险，投资需谨慎。

## 📄 License

[MIT](LICENSE)
