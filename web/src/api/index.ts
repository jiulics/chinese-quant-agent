import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 180000, // 分析可能较慢，放宽超时
})

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

export interface StockItem {
  symbol: string
  name: string
}

export async function analyzeStock(symbol: string, depth = 3): Promise<AnalyzeResult> {
  const { data } = await http.post<AnalyzeResult>('/analyze', { symbol, depth })
  return data
}

export async function searchStocks(q: string): Promise<StockItem[]> {
  const { data } = await http.get<StockItem[]>('/stocks/search', { params: { q } })
  return data
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const { data } = await http.get('/health')
  return data
}
