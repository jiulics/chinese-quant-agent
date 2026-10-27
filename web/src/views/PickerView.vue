<template>
  <div class="view">
    <div class="page-head">
      <h1>选股助手</h1>
      <p>按研究需求描述，智能匹配候选股票池</p>
    </div>

    <div class="input-row">
      <el-input
        v-model="need"
        placeholder="例如：寻找高股息、低估值、适合长期持有的蓝筹股"
        size="large"
        @keyup.enter="run"
      />
      <el-button type="primary" size="large" :loading="loading" @click="run">智能选股</el-button>
    </div>

    <div v-if="candidates.length" class="section">
      <h2>候选股票池（{{ candidates.length }}）</h2>
      <el-table :data="candidates" size="small" style="width:100%">
        <el-table-column prop="symbol" label="代码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column prop="change_pct" label="涨跌幅" width="100" />
      </el-table>
    </div>

    <el-card v-if="recommendation" class="result-card" shadow="never">
      <template #header><span class="card-title">智能推荐</span></template>
      <pre class="content">{{ recommendation }}</pre>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { pickStocks } from '@/api'
import { ElMessage } from 'element-plus'

const need = ref('')
const candidates = ref<any[]>([])
const recommendation = ref('')
const loading = ref(false)

async function run() {
  if (!need.value.trim()) return
  loading.value = true
  candidates.value = []
  recommendation.value = ''
  try {
    const r = await pickStocks(need.value.trim())
    candidates.value = r.candidates
    recommendation.value = r.recommendation
  } catch (e: any) {
    ElMessage.error(e?.message || '选股失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.input-row { display: flex; gap: 12px; margin-bottom: 20px; }
.section { margin-bottom: 20px; }
.section h2 { font-size: 16px; margin-bottom: 12px; }
.result-card { background: var(--card); border: 1px solid var(--border); }
.card-title { font-weight: 600; }
.content { white-space: pre-wrap; line-height: 1.8; font-size: 14px; color: var(--text); font-family: inherit; }
</style>
