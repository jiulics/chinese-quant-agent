import { http } from './http'

export async function chatAssistant(message: string, convId = 'default'): Promise<{ answer: string; tool_calls: any[]; facts: any[] }> {
  const { data } = await http.post('/assistant/chat', { message, conv_id: convId })
  return data
}

export async function listFacts(q?: string, limit = 50): Promise<any[]> {
  const { data } = await http.get('/memory/facts', { params: { q, limit } })
  return data
}
export async function addFact(content: string, source = '', tags: string[] = []): Promise<{ id: string }> {
  const { data } = await http.post('/memory/facts', { content, source, tags })
  return data
}
export async function deleteFact(fid: string): Promise<{ deleted: boolean }> {
  const { data } = await http.delete('/memory/facts/' + fid)
  return data
}
export async function memoryStats(): Promise<{ facts: number; sessions: number; conversations: number }> {
  const { data } = await http.get('/memory/stats')
  return data
}
