<template>
  <div class="kline-wrap">
    <!-- 当前行情头部 -->
    <div class="quote-head" v-if="quote && quote.price != null">
      <div class="q-name">{{ quote.name }} <span class="q-symbol">{{ quote.symbol }}</span></div>
      <div class="q-price" :class="quote.change_pct >= 0 ? 'up' : 'down'">
        {{ fmtPrice(quote.price) }}
      </div>
      <div class="q-chg" :class="quote.change_pct >= 0 ? 'up' : 'down'">
        {{ quote.change_pct >= 0 ? '+' : '' }}{{ fmt(quote.change_pct) }}%
        <span>{{ quote.change_pct >= 0 ? '+' : '' }}{{ fmt(quote.change) }}</span>
      </div>
      <div class="q-meta">
        <span>今开 {{ fmtPrice(quote.open) }}</span>
        <span>最高 <b class="up">{{ fmtPrice(quote.high) }}</b></span>
        <span>最低 <b class="down">{{ fmtPrice(quote.low) }}</b></span>
        <span>成交量 {{ fmtVol(quote.volume) }}</span>
        <span v-if="quote.timestamp" class="q-time">{{ fmtTs(quote.timestamp) }}</span>
      </div>
    </div>

    <!-- 周期切换器 -->
    <div class="period-bar">
      <span
        v-for="opt in periodOptions"
        :key="opt.value"
        class="period-btn"
        :class="{ active: period === opt.value }"
        @click="switchPeriod(opt.value)"
      >{{ opt.label }}</span>
    </div>

    <!-- K线图 -->
    <div ref="chartRef" class="kline-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  getKline, getRealtimeQuote, getIntraday,
  type KlineData, type RealtimeQuote, type IntradayData,
} from '@/api'

const props = defineProps<{ symbol: string }>()

const chartRef = ref<HTMLDivElement | null>(null)
const quote = ref<RealtimeQuote | null>(null)
const period = ref<'m5' | 'daily' | 'weekly' | 'monthly'>('daily')
const periodOptions: Array<{ value: 'm5' | 'daily' | 'weekly' | 'monthly'; label: string }> = [
  { value: 'm5', label: '分时' },
  { value: 'daily', label: '日K' },
  { value: 'weekly', label: '周K' },
  { value: 'monthly', label: '月K' },
]
let chart: echarts.ECharts | null = null
let resizeHandler: (() => void) | null = null

function fmtPrice(v: number | null | undefined): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function fmt(v: number | null | undefined): string {
  if (v === null || v === undefined) return '-'
  return Number(v).toFixed(2)
}
function fmtVol(v: number | null | undefined): string {
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (n >= 1e8) return (n / 1e8).toFixed(2) + ' 亿'
  if (n >= 1e4) return (n / 1e4).toFixed(2) + ' 万'
  return n.toFixed(0)
}
function fmtTs(ts?: string): string {
  if (!ts) return ''
  const s = String(ts)
  if (s.length === 14) return s.slice(8, 10) + ':' + s.slice(10, 12) + ':' + s.slice(12, 14)
  return s
}

const UP = '#f56c6c'
const DOWN = '#67c23a'

// 统一渲染：接收 dates/klines/ma 数组
function renderChart(dates: string[], klines: any[], ma: Record<string, (number | null)[]>, isCandle: boolean) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const volumes = klines.map((k) => ({
    value: k.volume,
    itemStyle: { color: k.close >= k.open ? UP : DOWN },
  }))

  const maSeries = Object.entries(ma).map(([name, data]) => ({
    name, type: 'line', data, smooth: true, showSymbol: false, lineStyle: { width: 1 },
  }))

  const mainSeries: any[] = isCandle
    ? [{
        name: 'K线', type: 'candlestick', data: klines.map(k => [k.open, k.close, k.low, k.high]),
        itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN },
      }, ...maSeries]
    : [{
        name: '价格', type: 'line', data: klines.map(k => k.close),
        showSymbol: false, smooth: true,
        lineStyle: { width: 1.5, color: '#409eff' },
        areaStyle: { color: 'rgba(64,158,255,0.08)' },
      }]

  const legendData = isCandle ? ['MA5', 'MA10', 'MA20', 'MA60'] : ['价格']

  chart.setOption({
    backgroundColor: 'transparent',
    animation: false,
    legend: { data: legendData, textStyle: { color: '#8b90a0' }, top: 0 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1a1e2a',
      borderColor: '#2a2f3e',
      textStyle: { color: '#e6e8ee' },
    },
    grid: [
      { left: 60, right: 20, top: 30, height: '58%' },
      { left: 60, right: 20, top: '74%', height: '16%' },
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLine: { lineStyle: { color: '#2a2f3e' } }, axisLabel: { color: '#8b90a0' } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#2a2f3e' } } },
    ],
    yAxis: [
      { scale: true, gridIndex: 0, axisLabel: { color: '#8b90a0' }, splitLine: { lineStyle: { color: '#1f2430' } } },
      { scale: true, gridIndex: 1, axisLabel: { color: '#8b90a0' }, splitLine: { show: false } },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: isCandle ? 60 : 0, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], top: '94%', height: 18, textStyle: { color: '#8b90a0' } },
    ],
    series: [
      ...mainSeries,
      { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumes },
    ],
  })
}

function fmtTimeLabel(t: string): string {
  // 202610191115 -> 10-19 11:15 ；分时 0930 -> 09:30
  if (t.length === 12) return t.slice(4, 6) + '-' + t.slice(6, 8) + ' ' + t.slice(8, 10) + ':' + t.slice(10, 12)
  if (t.length === 4) return t.slice(0, 2) + ':' + t.slice(2, 4)
  return t
}

async function loadIntraday() {
  const id: IntradayData = await getIntraday(props.symbol, 'm5')
  const dates = id.times.map(fmtTimeLabel)
  const klines = id.klines.map(k => ({
    open: k.open, close: k.close, high: k.high, low: k.low, volume: k.volume,
  }))
  // 分时图用收盘价折线 + 当日均价线（这里简化用 close）
  renderChart(dates, klines, {}, false)
}

async function loadKline() {
  const kd: KlineData = await getKline(props.symbol, 250, period.value as any)
  renderChart(kd.dates, kd.klines, {
    MA5: kd.ma5, MA10: kd.ma10, MA20: kd.ma20, MA60: kd.ma60,
  }, true)
}

async function load() {
  if (!props.symbol) return
  try {
    const q = await getRealtimeQuote(props.symbol)
    quote.value = q || null
    await nextTick()
    if (period.value === 'm5') {
      await loadIntraday()
    } else {
      await loadKline()
    }
  } catch {
    // 静默失败
  }
}

async function switchPeriod(p: 'm5' | 'daily' | 'weekly' | 'monthly') {
  period.value = p
  await nextTick()
  if (p === 'm5') await loadIntraday()
  else await loadKline()
}

onMounted(() => {
  load()
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  chart?.dispose()
  chart = null
})

watch(() => props.symbol, () => load())
</script>

<style scoped>
.kline-wrap {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;
}
.quote-head { display: flex; align-items: baseline; flex-wrap: wrap; gap: 14px; margin-bottom: 12px; }
.q-name { font-size: 16px; font-weight: 700; }
.q-symbol { font-size: 12px; color: var(--text-dim); font-weight: 400; margin-left: 6px; }
.q-price { font-size: 26px; font-weight: 800; }
.q-chg { font-size: 14px; font-weight: 600; }
.q-chg span { opacity: 0.7; margin-left: 6px; font-size: 12px; }
.q-meta { display: flex; gap: 14px; font-size: 12px; color: var(--text-dim); margin-left: auto; }
.q-meta b { font-weight: 600; }
.q-time { color: var(--text-dim); }
.up { color: var(--up); }
.down { color: var(--down); }
.period-bar { display: flex; gap: 6px; margin-bottom: 12px; }
.period-btn {
  padding: 4px 14px; font-size: 13px; cursor: pointer; border-radius: 8px;
  color: var(--text-dim); border: 1px solid var(--border);
  transition: all 0.2s; user-select: none;
}
.period-btn:hover { color: var(--text); border-color: var(--primary); }
.period-btn.active {
  color: #fff; background: var(--primary); border-color: var(--primary);
  font-weight: 600;
}
.kline-chart { width: 100%; height: 420px; }
</style>
