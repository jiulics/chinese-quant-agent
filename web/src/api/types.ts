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
  analyses_structured?: Array<{ role: string; content: string }>
  scenarios?: string | null
  final_signal: string
  depth: number
}

export interface StockItem {
  symbol: string
  name: string
}

export interface KlineItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  pct_chg: number | null
}

export interface KlineData {
  symbol: string
  name: string
  dates: string[]
  klines: KlineItem[]
  ma5: (number | null)[]
  ma10: (number | null)[]
  ma20: (number | null)[]
  ma60: (number | null)[]
}

export interface IntradayKline {
  time: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

export interface IntradayData {
  symbol: string
  period: string
  times: string[]
  klines: IntradayKline[]
}

export interface RealtimeQuote {
  symbol: string
  name: string
  price: number
  preclose: number | null
  open: number
  change: number
  change_pct: number
  high: number
  low: number
  volume: number
  amount: number
  timestamp: string
}

export interface MarketIndex {
  symbol: string
  name: string
  price?: number
  close?: number
  preclose: number
  change: number
  change_pct: number
  volume: number
  amount: number
  date?: string
  timestamp?: string
}

export type StreamEvent =
  | { type: 'stage'; stage: string; message: string }
  | { type: 'agent_start'; role: string; label?: string }
  | { type: 'agent_delta'; role: string; delta: string }
  | { type: 'agent_done'; role: string; content: string }
  | { type: 'final'; content: string }
  | { type: 'done'; symbol: string; final_signal: string; depth: number; scenarios?: string | null; quote: any; indicators: Record<string, any>; analyses: Array<{ role: string; content: string }> }
  | { type: 'error'; message: string }
