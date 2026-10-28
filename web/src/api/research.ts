import { http } from './http'
import type { AnalyzeResult, StockItem, MarketIndex, KlineData, RealtimeQuote, IntradayData } from './types'

export async function analyzeStock(symbol: string, depth = 3, useMock = false): Promise<AnalyzeResult> {
  const { data } = await http.post<AnalyzeResult>('/analyze', { symbol, depth, use_mock: useMock })
  return data
}

export async function getKline(symbol: string, days = 250, period = 'daily'): Promise<KlineData> {
  const { data } = await http.get<KlineData>(`/stocks/${symbol}/kline`, { params: { days, period } })
  return data
}

export async function getIntraday(symbol: string, period = 'm5'): Promise<IntradayData> {
  const { data } = await http.get<IntradayData>(`/stocks/${symbol}/intraday`, { params: { period } })
  return data
}

export async function getRealtimeQuote(symbol: string): Promise<RealtimeQuote> {
  const { data } = await http.get<RealtimeQuote>(`/stocks/${symbol}/realtime`)
  return data
}

export async function getMarketIndices(): Promise<MarketIndex[]> {
  const { data } = await http.get<MarketIndex[]>('/market/indices')
  return data
}

export async function searchStocks(q: string, useMock = false): Promise<StockItem[]> {
  const { data } = await http.get<StockItem[]>('/stocks/search', { params: { q, use_mock: useMock } })
  return data
}

export async function generalResearch(topic: string): Promise<{ topic: string; content: string }> {
  const { data } = await http.post('/research/general', { topic })
  return data
}

export async function screenStocks(query?: string, criteria?: Record<string, any>): Promise<{ items: any[]; total: number }> {
  const { data } = await http.post('/screener', { query, criteria })
  return data
}

export async function pickStocks(need: string): Promise<{ need: string; candidates: any[]; recommendation: string }> {
  const { data } = await http.post('/picker', { need })
  return data
}
