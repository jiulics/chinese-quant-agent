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

    <!-- K线图 -->
    <div ref="chartRef" class="kline-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getKline, getRealtimeQuote, type KlineData, type RealtimeQuote } from '@/api'

const props = defineProps<{ symbol: string }>()

const chartRef = ref<HTMLDivElement | null>(null)
const quote = ref<RealtimeQuote | null>(null)
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

function render(kd: KlineData) {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  const dates = kd.dates
  const klines = kd.klines
  const candles = klines.map(k => [k.open, k.close, k.low, k.high])
  const volumes = klines.map((k) => ({
    value: k.volume,
    itemStyle: { color: k.close >= k.open ? UP : DOWN },
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    animation: false,
    legend: {
      data: ['MA5', 'MA10', 'MA20', 'MA60'],
      textStyle: { color: '#8b90a0' },
      top: 0,
    },
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
      { type: 'inside', xAxisIndex: [0, 1], start: 60, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], top: '94%', height: 18, textStyle: { color: '#8b90a0' } },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: candles,
        itemStyle: {
          color: UP, color0: DOWN,
          borderColor: UP, borderColor0: DOWN,
        },
      },
      { name: 'MA5', type: 'line', data: kd.ma5, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MA10', type: 'line', data: kd.ma10, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MA20', type: 'line', data: kd.ma20, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
      { name: 'MA60', type: 'line', data: kd.ma60, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
      },
    ],
  })
}

async function load() {
  if (!props.symbol) return
  try {
    const [kd, q] = await Promise.all([
      getKline(props.symbol),
      getRealtimeQuote(props.symbol),
    ])
    quote.value = q || null
    await nextTick()
    render(kd)
  } catch {
    // 静默失败
  }
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
.kline-chart { width: 100%; height: 420px; }
</style>
