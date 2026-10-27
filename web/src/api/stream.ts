import type { StreamEvent } from './types'

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
