import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyzeStock, type AnalyzeResult } from '@/api'

export const useAnalysisStore = defineStore('analysis', () => {
  const loading = ref(false)
  const result = ref<AnalyzeResult | null>(null)
  const error = ref<string | null>(null)
  const currentSymbol = ref('')

  async function run(symbol: string) {
    loading.value = true
    error.value = null
    currentSymbol.value = symbol
    try {
      result.value = await analyzeStock(symbol)
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || '分析失败，请检查后端服务'
      result.value = null
    } finally {
      loading.value = false
    }
  }

  return { loading, result, error, currentSymbol, run }
})
