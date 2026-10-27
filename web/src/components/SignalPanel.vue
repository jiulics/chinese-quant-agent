<template>
  <div v-if="quote" class="quote-bar">
    <div class="q-name">{{ quote.name }}</div>
    <div class="q-price" :style="{ color: quote.change_pct >= 0 ? 'var(--up)' : 'var(--down)' }">
      {{ quote.price }}
    </div>
    <div class="q-pct" :style="{ color: quote.change_pct >= 0 ? 'var(--up)' : 'var(--down)' }">
      {{ quote.change_pct >= 0 ? '+' : '' }}{{ quote.change_pct }}%
    </div>
  </div>

  <div v-if="scenarios" class="panel-card">
    <div class="panel-head gold">
      <el-icon><Sunny /></el-icon><span>多情景观点</span>
    </div>
    <pre class="panel-text">{{ scenarios }}</pre>
  </div>

  <div v-if="finalSignal" class="panel-card">
    <div class="panel-head green">
      <el-icon><Trophy /></el-icon><span>最终投资信号</span>
    </div>
    <pre class="panel-text">{{ finalSignal }}</pre>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  quote: any
  scenarios: string | null
  finalSignal: string
}>()
</script>

<style scoped>
.quote-bar {
  display: flex; align-items: baseline; gap: 16px;
  padding: 18px 22px; background: var(--card);
  border: 1px solid var(--border); border-radius: 14px; margin-bottom: 20px;
}
.q-name { font-size: 18px; font-weight: 600; }
.q-price { font-size: 30px; font-weight: 700; }
.q-pct { font-size: 16px; font-weight: 600; }
.panel-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 18px; margin-top: 16px;
}
.panel-head { display: flex; align-items: center; gap: 10px; font-weight: 600; margin-bottom: 12px; }
.panel-head.gold { color: var(--gold); }
.panel-head.green { color: var(--down); }
.panel-text { white-space: pre-wrap; font-size: 13px; line-height: 1.7; color: var(--text); font-family: inherit; }
</style>
