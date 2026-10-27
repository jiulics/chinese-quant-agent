<template>
  <div class="search-bar">
    <el-select
      :model-value="symbol"
      filterable
      remote
      clearable
      placeholder="输入股票代码或名称"
      :remote-method="onSearch"
      :loading="searchLoading"
      class="symbol-select"
      @update:model-value="$emit('update:symbol', $event)"
    >
      <el-option v-for="s in searchResults" :key="s.symbol" :label="`${s.symbol} · ${s.name}`" :value="s.symbol" />
    </el-select>

    <div class="depth-select">
      <span class="label">分析深度</span>
      <el-radio-group :model-value="depth" size="small" @update:model-value="$emit('update:depth', $event)">
        <el-radio-button v-for="d in 5" :key="d" :value="d">{{ d }}级</el-radio-button>
      </el-radio-group>
    </div>

    <el-switch :model-value="useMock" active-text="演示数据" class="mock-switch" @update:model-value="$emit('update:useMock', $event)" />

    <el-button type="primary" :loading="loading" class="start-btn" @click="$emit('start')">
      <el-icon v-if="!loading"><CaretRight /></el-icon>
      {{ loading ? '分析中…' : '开始分析' }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { searchStocks, type StockItem } from '@/api'

const props = defineProps<{
  symbol: string
  depth: number
  useMock: boolean
  loading: boolean
}>()

defineEmits<{
  (e: 'update:symbol', v: string): void
  (e: 'update:depth', v: number): void
  (e: 'update:useMock', v: boolean): void
  (e: 'start'): void
}>()

const searchResults = ref<StockItem[]>([])
const searchLoading = ref(false)

async function onSearch(q: string) {
  if (!q) { searchResults.value = []; return }
  searchLoading.value = true
  try { searchResults.value = await searchStocks(q, props.useMock) } catch { searchResults.value = [] } finally { searchLoading.value = false }
}
</script>

<style scoped>
.search-bar {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  background: var(--card); border: 1px solid var(--border);
  padding: 16px; border-radius: 14px; margin-bottom: 20px;
}
.symbol-select { width: 300px; }
.depth-select { display: flex; align-items: center; gap: 10px; }
.depth-select .label { font-size: 13px; color: var(--text-dim); }
.start-btn { margin-left: auto; }
</style>
