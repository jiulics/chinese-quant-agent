import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 180000,
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
  analyses_structured?: Array<{ role: string; content: string }>
  scenarios?: string | null
  final_signal: string
  depth: number
}

export interface StockItem {
  symbol: string
  name: string
}

export async function analyzeStock(symbol: string, depth = 3, useMock = false): Promise<AnalyzeResult> {
  const { data } = await http.post<AnalyzeResult>('/analyze', { symbol, depth, use_mock: useMock })
  return data
}

export async function searchStocks(q: string, useMock = false): Promise<StockItem[]> {
  const { data } = await http.get<StockItem[]>('/stocks/search', { params: { q, use_mock: useMock } })
  return data
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const { data } = await http.get('/health')
  return data
}

// SSE 流式分析事件类型
export type StreamEvent =
  | { type: 'stage'; stage: string; message: string }
  | { type: 'agent_start'; role: string; label?: string }
  | { type: 'agent_delta'; role: string; delta: string }
  | { type: 'agent_done'; role: string; content: string }
  | { type: 'final'; content: string }
  | { type: 'done'; symbol: string; final_signal: string; depth: number; scenarios?: string | null; quote: any; indicators: Record<string, any>; analyses: Array<{ role: string; content: string }> }
  | { type: 'error'; message: string }

/**
 * 通过 SSE 流式分析股票，逐事件回调。
 * 返回一个取消函数。
 */
export function streamAnalyze(
  symbol: string,
  depth: number,
  useMock: boolean,
  onEvent: (ev: StreamEvent) => void,
  onDone: () => void,
): () => void {
  const controller = new AbortController()

  const run = async () => {
    try {
      const resp = await fetch('/api/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, depth, use_mock: useMock }),
        signal: controller.signal,
      })

      if (!resp.ok || !resp.body) {
        throw new Error('流式连接失败: ' + resp.status)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // 按 SSE 事件分隔（兼容 \n\n 与 \r\n\r\n）
        let idx: number
        while ((idx = buffer.search(/\r?\n\r?\n/)) !== -1) {
          const raw = buffer.slice(0, idx)
          buffer = buffer.slice(idx).replace(/^\r?\n\r?\n/, '')
          const dataLine = raw.split(/\r?\n/).find((l) => l.startsWith('data:'))
          if (!dataLine) continue
          const json = dataLine.slice(5).trim()
          try {
            const ev = JSON.parse(json) as StreamEvent
            onEvent(ev)
          } catch {
            // 忽略解析错误
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        onEvent({ type: 'error', message: e?.message || '流式分析失败' })
      }
    } finally {
      onDone()
    }
  }

  run()
  return () => controller.abort()
}
