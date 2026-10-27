<template>
  <div class="view">
    <div class="page-head">
      <h1>股票筛选</h1>
      <p>自然语言 + 条件筛选相结合，从 6000+ 只 A 股中发现标的</p>
    </div>

    <div class="input-row">
      <el-input v-model="query" placeholder="例如：市盈率低于20倍且连续上涨的银行股" size="large" @keyup.enter="runNatural" />
      <el-button type="primary" size="large" :loading="loading" @click="runNatural">智能筛选</el-button>
    </div>

    <div class="filters">
      <el-input v-model="criteria.keyword" placeholder="关键词" size="small" style="width:160px" />
      <el-input v-model="criteria.industry" placeholder="行业" size="small" style="width:160px" />
      <el-input-number v-model="criteria.min_price" :min="0" :controls="false" placeholder="最低价" size="small" />
      <el-input-number v-model="criteria.max_price" :min="0" :controls="false" placeholder="最高价" size="small" />
      <el-button size="small" @click="runCriteria">条件筛选</el-button>
    </div>

    <el-table v-if="items.length" :data="items" size="small" style="width:100%" class="result-table">
      <el-table-column prop="symbol" label="代码" width="120" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="change_pct" label="涨跌幅" width="100" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { screenStocks } from '@/api'
import { ElMessage } from 'element-plus'

const query = ref('')
const items = ref<any[]>([])
const loading = ref(false)
const criteria = reactive<Record<string, any>>({ keyword: '', industry: '' })

async function runNatural() {
  if (!query.value.trim()) return
  loading.value = true
  try {
    const r = await screenStocks(query.value.trim())
    items.value = r.items
  } catch (e: any) {
    ElMessage.error(e?.message || '筛选失败')
  } finally {
    loading.value = false
  }
}

async function runCriteria() {
  loading.value = true
  try {
    const c: Record<string, any> = {}
    if (criteria.keyword) c.keyword = criteria.keyword
    if (criteria.industry) c.industry = criteria.industry
    if (criteria.min_price) c.min_price = criteria.min_price
    if (criteria.max_price) c.max_price = criteria.max_price
    const r = await screenStocks(undefined, c)
    items.value = r.items
  } catch (e: any) {
    ElMessage.error(e?.message || '筛选失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.input-row { display: flex; gap: 12px; margin-bottom: 16px; }
.filters { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
.result-table { margin-top: 8px; }
</style>
