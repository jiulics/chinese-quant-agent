import { defineStore } from 'pinia'
import { ref } from 'vue'
import { streamAnalyze, type StreamEvent } from '@/api'

export interface AgentProgress {
  role: string
  label: string
  content: string
  done: boolean
  active: boolean      // 是否正在流式输出（当前焦点）
  order: number        // 出现顺序
}

export const useAnalysisStore = defineStore('analysis', () => {
  const loading = ref(false)
  const currentSymbol = ref('')
  const depth = ref(3)
  const stage = ref('')
  const stageMessage = ref('')
  const agents = ref<AgentProgress[]>([])
  const scenarios = ref<string | null>(null)
  const finalSignal = ref('')
  const quote = ref<any>(null)
  const indicators = ref<Record<string, any>>({})
  const error = ref<string | null>(null)
  const activeRole = ref('')   // 当前正在流式的角色

  let cancelFn: (() => void) | null = null

  const ROLE_LABELS: Record<string, string> = {
    analyst: '基本面分析师',
    technical: '技术面分析师',
    risk: '风控分析师',
    strategist: '策略师',
    moderator: '辩论主持人',
    scenario: '情景分析师',
  }

  function reset() {
    stage.value = ''
    stageMessage.value = ''
    agents.value = []
    scenarios.value = null
    finalSignal.value = ''
    quote.value = null
    indicators.value = {}
    error.value = null
    activeRole.value = ''
  }

  function ensureAgent(role: string, label: string): AgentProgress {
    let a = agents.value.find((x) => x.role === role)
    if (!a) {
      a = {
        role,
        label: label || ROLE_LABELS[role] || role,
        content: '',
        done: false,
        active: false,
        order: agents.value.length,
      }
      agents.value.push(a)
    }
    return a
  }

  function handleEvent(ev: StreamEvent) {
    switch (ev.type) {
      case 'stage':
        stage.value = ev.stage
        stageMessage.value = ev.message
        break
      case 'agent_start': {
        const a = ensureAgent(ev.role, ev.label || ROLE_LABELS[ev.role] || ev.role)
        a.done = false
        a.active = true
        activeRole.value = ev.role
        break
      }
      case 'agent_delta': {
        const a = ensureAgent(ev.role, '')
        a.content += ev.delta
        break
      }
      case 'agent_done': {
        const a = ensureAgent(ev.role, '')
        a.content = ev.content
        a.done = true
        a.active = false
        if (activeRole.value === ev.role) activeRole.value = ''
        break
      }
      case 'final':
        finalSignal.value = ev.content
        break
      case 'done':
        finalSignal.value = ev.final_signal
        scenarios.value = ev.scenarios ?? null
        quote.value = ev.quote
        indicators.value = ev.indicators
        break
      case 'error':
        error.value = ev.message
        break
    }
  }

  function run(symbol: string, d: number, useMock = false) {
    reset()
    loading.value = true
    currentSymbol.value = symbol
    depth.value = d

    cancelFn = streamAnalyze(
      symbol,
      d,
      useMock,
      (ev) => handleEvent(ev),
      () => {
        loading.value = false
      },
    )
  }

  function cancel() {
    cancelFn?.()
    cancelFn = null
    loading.value = false
  }

  return {
    loading, currentSymbol, depth, stage, stageMessage,
    agents, scenarios, finalSignal, quote, indicators, error,
    activeRole, run, cancel, reset,
  }
})
