import { http } from './http'

export async function listSkills(): Promise<any[]> {
  const { data } = await http.get('/skills')
  return data
}
export async function runSkill(name: string, kwargs: Record<string, any> = {}): Promise<{ result: string }> {
  const { data } = await http.post('/skills/' + name + '/run', { kwargs })
  return data
}

export async function tradingSnapshot(): Promise<any> {
  const { data } = await http.get('/trading/snapshot')
  return data
}
export async function tradeOrder(side: 'buy' | 'sell', symbol: string, quantity: number): Promise<any> {
  const { data } = await http.post('/trading/' + side, { symbol, quantity })
  return data
}
export async function tradingOrders(limit = 50): Promise<any[]> {
  const { data } = await http.get('/trading/orders', { params: { limit } })
  return data
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const { data } = await http.get('/health')
  return data
}
