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

export type StreamEvent =
  | { type: 'stage'; stage: string; message: string }
  | { type: 'agent_start'; role: string; label?: string }
  | { type: 'agent_delta'; role: string; delta: string }
  | { type: 'agent_done'; role: string; content: string }
  | { type: 'final'; content: string }
  | { type: 'done'; symbol: string; final_signal: string; depth: number; scenarios?: string | null; quote: any; indicators: Record<string, any>; analyses: Array<{ role: string; content: string }> }
  | { type: 'error'; message: string }
