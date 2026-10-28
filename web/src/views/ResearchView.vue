<template>
  <div class="research">
    <div class="page-head">
      <h1>单股研究</h1>
      <p>多智能体辩论式分析 · 分析师依次登场，实时呈现推理过程</p>
    </div>

    <MarketBoard />

    <StockSearchBar
      v-model:symbol="symbol"
      v-model:depth="depth"
      v-model:use-mock="useMock"
      :loading="store.loading"
      @start="start"
    />

    <KlineChart v-if="symbol" :symbol="symbol" />

    <transition name="fade">
      <div v-if="store.stage" class="stage-banner">
        <el-icon class="stage-icon"><Loading /></el-icon>
        <div>
          <div class="stage-title">{{ store.stage }}</div>
          <div class="stage-msg">{{ store.stageMessage }}</div>
        </div>
      </div>
    </transition>

    <div v-if="store.agents.length" class="agents-list">
      <div class="list-head">
        <span>分析师辩论序列</span>
        <span class="progress">{{ doneCount }} / {{ store.agents.length }}</span>
      </div>
      <AgentCard v-for="a in store.agents" :key="a.role" :agent="a" />
    </div>

    <SignalPanel
      :quote="store.quote"
      :scenarios="store.scenarios"
      :final-signal="store.finalSignal"
    />

    <el-alert v-if="store.error" :title="store.error" type="error" show-icon :closable="false" class="err" />

    <div v-if="!store.loading && !store.agents.length && !store.error" class="empty">
      <el-icon size="60" color="#3a4050"><TrendCharts /></el-icon>
      <p>输入股票代码，开始多智能体辩论式分析</p>
      <div class="hot">
        <el-tag v-for="s in hot" :key="s" class="hot-tag" @click="symbol = s; start()">{{ s }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import StockSearchBar from '@/components/StockSearchBar.vue'
import AgentCard from '@/components/AgentCard.vue'
import SignalPanel from '@/components/SignalPanel.vue'
import MarketBoard from '@/components/MarketBoard.vue'
import KlineChart from '@/components/KlineChart.vue'

const store = useAnalysisStore()
const route = useRoute()
const symbol = ref('')
const depth = ref(3)
const useMock = ref(false)
const hot = ['600519', '000001', '300750', '601318']

const doneCount = computed(() => store.agents.filter((a) => a.done).length)

function start() {
  if (!symbol.value.trim()) return
  store.run(symbol.value.trim(), depth.value, useMock.value)
}

onMounted(() => {
  const q = route.query.symbol as string | undefined
  if (q) {
    symbol.value = q
    start()
  }
})
</script>

<style scoped>
.research { max-width: 860px; margin: 0 auto; }
.page-head h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.stage-banner {
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(90deg, rgba(64,158,255,0.15), rgba(124,92,255,0.1));
  border: 1px solid rgba(64,158,255,0.3); border-radius: 12px;
  padding: 14px 18px; margin-bottom: 20px;
}
.stage-icon { color: var(--primary); font-size: 20px; animation: spin 1.2s linear infinite; }
.stage-title { font-weight: 600; font-size: 14px; }
.stage-msg { color: var(--text-dim); font-size: 12px; margin-top: 2px; }
@keyframes spin { to { transform: rotate(360deg); } }
.agents-list { display: flex; flex-direction: column; gap: 12px; }
.list-head {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; color: var(--text-dim); padding: 0 4px;
}
.progress { font-weight: 600; color: var(--primary); }
.err { margin-top: 16px; }
.empty { text-align: center; padding: 80px 0; color: var(--text-dim); }
.empty p { margin: 16px 0; }
.hot { display: flex; gap: 8px; justify-content: center; }
.hot-tag { cursor: pointer; }
</style>
