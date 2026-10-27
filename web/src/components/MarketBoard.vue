<template>
  <div class="market-board" v-if="indices.length">
    <div class="board-head">
      <el-icon><DataLine /></el-icon>
      <span>大盘指数</span>
      <span class="date">{{ indices[0]?.date }}</span>
      <el-icon class="refresh" :class="{ spinning: loading }" @click="load"><Refresh /></el-icon>
    </div>
    <div class="index-grid">
      <div
        v-for="idx in indices"
        :key="idx.symbol"
        class="index-card"
        :class="{ up: idx.change_pct >= 0, down: idx.change_pct < 0 }"
      >
        <div class="idx-name">{{ idx.name }}</div>
        <div class="idx-close">{{ fmt(idx.close) }}</div>
        <div class="idx-change">
          {{ idx.change_pct >= 0 ? '+' : '' }}{{ fmt(idx.change_pct) }}%
          <span class="idx-diff">{{ idx.change_pct >= 0 ? '+' : '' }}{{ fmt(idx.change) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMarketIndices, type MarketIndex } from '@/api'

const indices = ref<MarketIndex[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    indices.value = await getMarketIndices()
  } catch {
    indices.value = []
  } finally {
    loading.value = false
  }
}

function fmt(v: number | null | undefined): string {
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (Number.isNaN(n)) return '-'
  // 指数保留 2 位，涨跌幅保留 2 位
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(load)
</script>

<style scoped>
.market-board {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;
}
.board-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-dim); margin-bottom: 14px;
}
.board-head > span:first-of-type { color: var(--text); font-weight: 600; }
.date { margin-left: auto; font-size: 12px; }
.refresh { cursor: pointer; color: var(--text-dim); transition: color 0.2s; }
.refresh:hover { color: var(--primary); }
.spinning { animation: spin 1s linear infinite; }
.index-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px;
}
.index-card {
  background: var(--bg-soft); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 14px; transition: all 0.2s;
}
.index-card:hover { border-color: var(--primary); }
.idx-name { font-size: 12px; color: var(--text-dim); margin-bottom: 6px; }
.idx-close { font-size: 20px; font-weight: 700; }
.idx-change { font-size: 12px; font-weight: 600; margin-top: 4px; }
.idx-diff { margin-left: 6px; opacity: 0.7; }
.index-card.up .idx-close, .index-card.up .idx-change { color: var(--up); }
.index-card.down .idx-close, .index-card.down .idx-change { color: var(--down); }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
