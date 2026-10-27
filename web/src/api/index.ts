import axios from 'axios'

// 统一的后端 API 客户端
const http = axios.create({
  baseURL: '/api',
  timeout: 120000, // 分析可能较慢，放宽超时
})

// 类型定义
export interface StockQuote {
  symbol: string
  name: string
  price: number
  change: number
  change_pct: number
  open: number
  high: number
  low: number
  volume: number
  amount: number
  timestamp: string
}

export interface AnalyzeResult {
  symbol: string
  quote: StockQuote
  indicators: Record<string, number | number[]>
  analyses: string[]
  final_signal: string
}

// 分析单只股票
export async function analyzeStock(symbol: string): Promise<AnalyzeResult> {
  const { data } = await http.post<AnalyzeResult>('/analyze', { symbol })
  return data
}

// 获取股票列表（用于搜索联想）
export async function getStockList(): Promise<Array<{ symbol: string; name: string }>> {
  const { data } = await http.get<Array<{ symbol: string; name: string }>>('/stocks')
  return data
}
