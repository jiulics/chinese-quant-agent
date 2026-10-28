<template>
  <div class="dashboard">
    <div class="page-head">
      <h1>市场总览</h1>
      <p>大盘指数与市场快照 · 数据来源 BaoStock 实时行情</p>
    </div>

    <MarketBoard />

    <div class="hot-section">
      <div class="section-head">
        <el-icon><Star /></el-icon>
        <span>热门标的 · 快速分析</span>
      </div>
      <div class="hot-grid">
        <div
          v-for="s in hotStocks"
          :key="s.symbol"
          class="hot-card"
          @click="goResearch(s.symbol)"
        >
          <div class="hot-symbol">{{ s.symbol }}</div>
          <div class="hot-name">{{ s.name }}</div>
          <el-icon class="hot-arrow"><Right /></el-icon>
        </div>
      </div>
    </div>

    <div v-if="favs.length" class="hot-section watchlist-section">
      <div class="section-head">
        <el-icon><StarFilled /></el-icon>
        <span>我的自选</span>
      </div>
      <div class="hot-grid">
        <div
          v-for="s in favs"
          :key="s"
          class="hot-card"
          @click="goResearch(s)"
        >
          <div class="hot-symbol">{{ s }}</div>
          <el-icon class="hot-arrow"><Right /></el-icon>
        </div>
      </div>
    </div>

    <div class="tip">
      <el-icon><InfoFilled /></el-icon>
      <span>点击任意标的进入多智能体辩论式分析；以上指数为最新交易日收盘快照。</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import MarketBoard from '@/components/MarketBoard.vue'

const router = useRouter()
const FAV_KEY = 'watchlist'
const favs = ref<string[]>(JSON.parse(localStorage.getItem(FAV_KEY) || '[]'))

function refreshFavs() {
  favs.value = JSON.parse(localStorage.getItem(FAV_KEY) || '[]')
}

onMounted(() => {
  window.addEventListener('watchlist-changed', refreshFavs)
})
onUnmounted(() => {
  window.removeEventListener('watchlist-changed', refreshFavs)
})

const hotStocks = [
  { symbol: '600519', name: '贵州茅台' },
  { symbol: '000001', name: '平安银行' },
  { symbol: '300750', name: '宁德时代' },
  { symbol: '601318', name: '中国平安' },
  { symbol: '000858', name: '五粮液' },
  { symbol: '600036', name: '招商银行' },
  { symbol: '002594', name: '比亚迪' },
  { symbol: '601899', name: '紫金矿业' },
]

function goResearch(symbol: string) {
  router.push({ path: '/research', query: { symbol } })
}
</script>

<style scoped>
.dashboard { max-width: 1100px; margin: 0 auto; }
.page-head h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.hot-section { margin-top: 8px; }
.section-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 12px;
}
.section-head .el-icon { color: var(--gold); }
.hot-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.hot-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px; cursor: pointer;
  display: flex; flex-direction: column; gap: 6px; transition: all 0.2s;
  position: relative;
}
.hot-card:hover { border-color: var(--primary); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
.hot-symbol { font-size: 16px; font-weight: 700; color: var(--primary); }
.hot-name { font-size: 13px; color: var(--text); }
.hot-arrow { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-dim); }
.tip {
  display: flex; align-items: center; gap: 8px; margin-top: 20px;
  font-size: 12px; color: var(--text-dim); background: var(--bg-soft);
  border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px;
}
.tip .el-icon { color: var(--primary); }
</style>
