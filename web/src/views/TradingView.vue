<template>
  <div class="view">
    <div class="page-head">
      <h1>模拟交易</h1>
      <p>纸面交易：虚拟买卖、持仓管理与复盘</p>
    </div>

    <div class="stats">
      <div class="stat-card"><div class="num">{{ fmt(snap.cash) }}</div><div class="lbl">可用现金</div></div>
      <div class="stat-card"><div class="num">{{ fmt(snap.market_value) }}</div><div class="lbl">总资产</div></div>
      <div class="stat-card"><div class="num" :style="{color: snap.total_pnl >= 0 ? 'var(--up)' : 'var(--down)'}">{{ fmt(snap.total_pnl) }}</div><div class="lbl">浮动盈亏</div></div>
      <div class="stat-card"><div class="num" :style="{color: snap.total_return_pct >= 0 ? 'var(--up)' : 'var(--down)'}">{{ snap.total_return_pct }}%</div><div class="lbl">收益率</div></div>
    </div>

    <div class="input-row">
      <el-input v-model="symbol" placeholder="股票代码，如 600519" size="large" style="width:200px" />
      <el-input-number v-model="quantity" :min="100" :step="100" size="large" placeholder="数量" />
      <el-button type="success" size="large" :loading="loading" @click="order('buy')">买入</el-button>
      <el-button type="danger" size="large" :loading="loading" @click="order('sell')">卖出</el-button>
    </div>

    <h2 v-if="snap.positions?.length" class="section-title">当前持仓</h2>
    <el-table v-if="snap.positions?.length" :data="snap.positions" size="small" style="width:100%">
      <el-table-column prop="symbol" label="代码" width="120" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column prop="avg_cost" label="成本价" width="100" />
      <el-table-column prop="price" label="现价" width="100" />
      <el-table-column prop="pnl" label="盈亏" width="120">
        <template #default="{ row }"><span :style="{color: row.pnl >= 0 ? 'var(--up)' : 'var(--down)'}">{{ fmt(row.pnl) }}</span></template>
      </el-table-column>
    </el-table>

    <h2 v-if="orders.length" class="section-title">交易记录</h2>
    <el-table v-if="orders.length" :data="orders" size="small" style="width:100%">
      <el-table-column prop="side" label="方向" width="80">
        <template #default="{ row }"><el-tag :type="row.side === 'buy' ? 'success' : 'danger'" size="small">{{ row.side === 'buy' ? '买入' : '卖出' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="symbol" label="代码" width="110" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="quantity" label="数量" width="90" />
      <el-table-column prop="price" label="成交价" width="100" />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at * 1000).toLocaleString() }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { tradingSnapshot, tradeOrder, tradingOrders } from '@/api'
import { ElMessage } from 'element-plus'

const symbol = ref('')
const quantity = ref(100)
const loading = ref(false)
const snap = reactive<any>({ cash: 0, market_value: 0, total_pnl: 0, total_return_pct: 0, positions: [] })
const orders = ref<any[]>([])

async function refresh() {
  Object.assign(snap, await tradingSnapshot())
  orders.value = await tradingOrders()
}

async function order(side: 'buy' | 'sell') {
  if (!symbol.value.trim()) { ElMessage.warning('请输入股票代码'); return }
  loading.value = true
  try {
    const r = await tradeOrder(side, symbol.value.trim(), quantity.value)
    if (r.error) { ElMessage.error(r.error) } else { ElMessage.success(side === 'buy' ? '买入成功' : '卖出成功') }
    await refresh()
  } catch (e: any) {
    ElMessage.error(e?.message || '交易失败')
  } finally {
    loading.value = false
  }
}

function fmt(n: number) {
  return n?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(refresh)
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.stats { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; text-align: center; }
.num { font-size: 26px; font-weight: 700; }
.lbl { color: var(--text-dim); font-size: 13px; margin-top: 4px; }
.input-row { display: flex; gap: 12px; margin-bottom: 24px; }
.section-title { font-size: 16px; margin-bottom: 12px; }
</style>
