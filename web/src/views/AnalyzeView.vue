<template>
  <div class="analyze-page">
    <el-container>
      <el-header class="header">
        <div class="brand">
          <el-icon size="24"><TrendCharts /></el-icon>
          <span>chinese-quant-agent</span>
        </div>
        <span class="subtitle">中文金融多智能体交易框架</span>
      </el-header>

      <el-main>
        <el-card class="search-card">
          <el-form :inline="true" @submit.prevent="onSubmit">
            <el-form-item label="股票代码">
              <el-input
                v-model="symbol"
                placeholder="输入股票代码，如 600519"
                clearable
                style="width: 260px"
                @keyup.enter="onSubmit"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="store.loading"
                @click="onSubmit"
              >
                开始分析
              </el-button>
            </el-form-item>
          </el-form>
          <div class="quick-tags">
            <el-tag
              v-for="s in quickSymbols"
              :key="s"
              class="tag"
              effect="plain"
              @click="symbol = s; onSubmit()"
            >
              {{ s }}
            </el-tag>
          </div>
        </el-card>

        <el-alert
          v-if="store.error"
          :title="store.error"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />

        <div v-if="store.result" class="result">
          <!-- 行情概览 -->
          <el-card class="block">
            <template #header>
              <div class="block-header">
                <span>行情概览</span>
                <el-tag :type="pctType" effect="dark">
                  {{ store.result.quote.change_pct }}%
                </el-tag>
              </div>
            </template>
            <div class="quote-grid">
              <div class="quote-item">
                <div class="label">股票名称</div>
                <div class="value">{{ store.result.quote.name }}</div>
              </div>
              <div class="quote-item">
                <div class="label">最新价</div>
                <div class="value big">{{ store.result.quote.price }}</div>
              </div>
              <div class="quote-item">
                <div class="label">涨跌额</div>
                <div class="value">{{ store.result.quote.change }}</div>
              </div>
              <div class="quote-item">
                <div class="label">今开 / 最高 / 最低</div>
                <div class="value">
                  {{ store.result.quote.open }} / {{ store.result.quote.high }} / {{ store.result.quote.low }}
                </div>
              </div>
              <div class="quote-item">
                <div class="label">成交量</div>
                <div class="value">{{ formatVolume(store.result.quote.volume) }}</div>
              </div>
              <div class="quote-item">
                <div class="label">成交额</div>
                <div class="value">{{ formatAmount(store.result.quote.amount) }}</div>
              </div>
            </div>
          </el-card>

          <!-- 技术指标 -->
          <el-card class="block">
            <template #header><span>技术指标</span></template>
            <div class="indicator-grid">
              <div
                v-for="(v, k) in store.result.indicators"
                :key="k"
                class="indicator-item"
              >
                <div class="label">{{ k }}</div>
                <div class="value">{{ Array.isArray(v) ? v.join(', ') : v }}</div>
              </div>
            </div>
          </el-card>

          <!-- 分析报告 -->
          <el-card
            v-for="(a, i) in store.result.analyses"
            :key="i"
            class="block"
          >
            <template #header><span>分析报告 {{ i + 1 }}</span></template>
            <div class="analysis-text">{{ a }}</div>
          </el-card>

          <!-- 最终信号 -->
          <el-card class="block final-card">
            <template #header>
              <span class="final-title">最终投资信号</span>
            </template>
            <div class="analysis-text final-text">{{ store.result.final_signal }}</div>
          </el-card>
        </div>

        <el-empty v-else-if="!store.loading" description="输入股票代码开始分析" />
      </el-main>

      <el-footer class="footer">
        ⚠️ 内容仅供参考，不构成投资建议。股市有风险，投资需谨慎。
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'

const store = useAnalysisStore()
const symbol = ref('')

const quickSymbols = ['600519', '000001', '300750', '601318']

const pctType = computed(() => {
  const pct = store.result?.quote.change_pct ?? 0
  if (pct > 0) return 'danger'
  if (pct < 0) return 'success'
  return 'info'
})

function onSubmit() {
  const s = symbol.value.trim()
  if (!s) return
  store.run(s)
}

function formatVolume(v: number): string {
  if (v >= 1e8) return (v / 1e8).toFixed(2) + ' 亿手'
  if (v >= 1e4) return (v / 1e4).toFixed(2) + ' 万手'
  return String(v)
}

function formatAmount(v: number): string {
  if (v >= 1e8) return (v / 1e8).toFixed(2) + ' 亿元'
  if (v >= 1e4) return (v / 1e4).toFixed(2) + ' 万元'
  return String(v)
}
</script>

<style scoped>
.analyze-page {
  min-height: 100vh;
  background: #f5f7fa;
}
.header {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #1f2937;
  color: #fff;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 18px;
}
.subtitle {
  font-size: 13px;
  opacity: 0.8;
}
.search-card {
  margin-bottom: 16px;
}
.quick-tags {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.tag {
  cursor: pointer;
}
.error-alert {
  margin-bottom: 16px;
}
.block {
  margin-bottom: 16px;
}
.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quote-grid,
.indicator-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}
.quote-item .label,
.indicator-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}
.quote-item .value,
.indicator-item .value {
  font-size: 15px;
  color: #303133;
  word-break: break-all;
}
.value.big {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}
.analysis-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #303133;
}
.final-card {
  border: 1px solid #67c23a;
}
.final-title {
  color: #67c23a;
  font-weight: 700;
}
.final-text {
  font-size: 15px;
}
.footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  line-height: 40px;
}
</style>
