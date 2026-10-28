<template>
  <div class="kline-wrap">
    <!-- 当前行情头部 -->
    <div class="quote-head" v-if="quote && quote.price != null">
      <div class="q-name">
        {{ quote.name }} <span class="q-symbol">{{ quote.symbol }}</span>
        <span class="fav" :class="{ on: isFav }" @click="toggleFav">
          {{ isFav ? '★ 已自选' : '☆ 加自选' }}
        </span>
      </div>
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

    <!-- 周期 + 副图指标切换器 -->
    <div class="bar">
      <div class="period-bar">
        <span
          v-for="opt in periodOptions"
          :key="opt.value"
          class="bar-btn"
          :class="{ active: period === opt.value }"
          @click="switchPeriod(opt.value)"
        >{{ opt.label }}</span>
      </div>
      <div class="indicator-bar">
        <span
          v-for="opt in indicatorOptions"
          :key="opt.value"
          class="bar-btn"
          :class="{ active: indicator === opt.value }"
          @click="switchIndicator(opt.value)"
        >{{ opt.label }}</span>
      </div>
    </div>

    <!-- K线图 -->
    <div ref="chartRef" class="kline-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import {
  getKline, getRealtimeQuote, getIntraday,
  type KlineData, type RealtimeQuote, type IntradayData,
} from '@/api'

const props = defineProps<{ symbol: string }>()

const chartRef = ref<HTMLDivElement | null>(null)
const quote = ref<RealtimeQuote | null>(null)
const period = ref<'m5' | 'daily' | 'weekly' | 'monthly'>('daily')
const indicator = ref<'vol' | 'macd' | 'kdj' | 'rsi'>('vol')

const periodOptions: Array<{ value: 'm5' | 'daily' | 'weekly' | 'monthly'; label: string }> = [
  { value: 'm5', label: '分时' },
  { value: 'daily', label: '日K' },
  { value: 'weekly', label: '周K' },
  { value: 'monthly', label: '月K' },
]
const indicatorOptions: Array<{ value: 'vol' | 'macd' | 'kdj' | 'rsi'; label: string }> = [
  { value: 'vol', label: '成交量' },
  { value: 'macd', label: 'MACD' },
  { value: 'kdj', label: 'KDJ' },
  { value: 'rsi', label: 'RSI' },
]

let chart: echarts.ECharts | null = null
let resizeHandler: (() => void) | null = null

// 多周期数据缓存：切换周期时命中缓存则零网络、瞬间切换
interface CachedPeriod {
  dates: string[]
  klines: any[]
  kd: KlineData | null   // 有均线/指标序列（日/周/月K）
  isCandle: boolean
}
const periodCache = new Map<string, CachedPeriod>()
let loadingPeriods = new Set<string>()

// 自选股（localStorage）
const FAV_KEY = 'watchlist'
const favs = ref<string[]>(JSON.parse(localStorage.getItem(FAV_KEY) || '[]'))
const isFav = computed(() => favs.value.includes(props.symbol))
function toggleFav() {
  if (isFav.value) {
    favs.value = favs.value.filter(s => s !== props.symbol)
  } else {
    favs.value = [...favs.value, props.symbol]
  }
  localStorage.setItem(FAV_KEY, JSON.stringify(favs.value))
  window.dispatchEvent(new CustomEvent('watchlist-changed'))
}

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

function fmtTimeLabel(t: string): string {
  if (t.length === 12) return t.slice(4, 6) + '-' + t.slice(6, 8) + ' ' + t.slice(8, 10) + ':' + t.slice(10, 12)
  if (t.length === 4) return t.slice(0, 2) + ':' + t.slice(2, 4)
  return t
}

// ---- 数据加载（带缓存）----
async function fetchPeriod(p: 'm5' | 'daily' | 'weekly' | 'monthly'): Promise<CachedPeriod> {
  if (p === 'm5') {
    const id: IntradayData = await getIntraday(props.symbol, 'm5')
    const dates = id.times.map(fmtTimeLabel)
    const klines = id.klines.map(k => ({ open: k.open, close: k.close, high: k.high, low: k.low, volume: k.volume }))
    return { dates, klines, kd: null, isCandle: false }
  }
  const kd: KlineData = await getKline(props.symbol, 250, p as any)
  return { dates: kd.dates, klines: kd.klines, kd, isCandle: true }
}

// ---- 副图指标序列构建（只产 series，主图不动）----
function buildSubSeries(ind: string, kd: KlineData | null, klines: any[]): any[] {
  if (ind === 'macd' && kd?.macd) {
    return [
      { id: 'sub-dif', name: 'DIF', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.macd.dif, showSymbol: false, lineStyle: { width: 1, color: '#e6a23c' } },
      { id: 'sub-dea', name: 'DEA', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.macd.dea, showSymbol: false, lineStyle: { width: 1, color: '#409eff' } },
      { id: 'sub-macd', name: 'MACD', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: kd.macd.macd, itemStyle: { color: (p: any) => (p.value >= 0 ? UP : DOWN) } },
    ]
  }
  if (ind === 'kdj' && kd?.kdj) {
    return [
      { id: 'sub-k', name: 'K', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.kdj.k, showSymbol: false, lineStyle: { width: 1, color: '#e6a23c' } },
      { id: 'sub-d', name: 'D', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.kdj.d, showSymbol: false, lineStyle: { width: 1, color: '#409eff' } },
      { id: 'sub-j', name: 'J', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.kdj.j, showSymbol: false, lineStyle: { width: 1, color: '#f56c6c' } },
    ]
  }
  if (ind === 'rsi' && kd?.rsi) {
    return [
      { id: 'sub-rsi', name: 'RSI14', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: kd.rsi, showSymbol: false, lineStyle: { width: 1, color: '#67c23a' } },
    ]
  }
  // 默认成交量
  return [{
    id: 'sub-vol', name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
    data: klines.map((k) => ({ value: k.volume, itemStyle: { color: k.close >= k.open ? UP : DOWN } })),
  }]
}

function subLegend(ind: string): string[] {
  if (ind === 'macd') return ['DIF', 'DEA', 'MACD']
  if (ind === 'kdj') return ['K', 'D', 'J']
  if (ind === 'rsi') return ['RSI14']
  return ['成交量']
}

// ---- 主图 series（含均线）----
function buildMainSeries(cp: CachedPeriod): any[] {
  if (!cp.isCandle) {
    return [{
      id: 'main-price', name: '价格', type: 'line', data: cp.klines.map(k => k.close),
      showSymbol: false, smooth: true,
      lineStyle: { width: 1.5, color: '#409eff' },
      areaStyle: { color: 'rgba(64,158,255,0.08)' },
    }]
  }
  const kd = cp.kd!
  return [
    { id: 'main-candle', name: 'K线', type: 'candlestick', data: cp.klines.map(k => [k.open, k.close, k.low, k.high]), itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN } },
    { id: 'ma5', name: 'MA5', type: 'line', data: kd.ma5, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
    { id: 'ma10', name: 'MA10', type: 'line', data: kd.ma10, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
    { id: 'ma20', name: 'MA20', type: 'line', data: kd.ma20, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
    { id: 'ma60', name: 'MA60', type: 'line', data: kd.ma60, smooth: true, showSymbol: false, lineStyle: { width: 1 } },
  ]
}

function mainLegend(cp: CachedPeriod): string[] {
  return cp.isCandle ? ['MA5', 'MA10', 'MA20', 'MA60'] : ['价格']
}

// ---- 完整渲染（首次/切周期时调用）----
function renderFull(cp: CachedPeriod, ind: string) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const sub = buildSubSeries(ind, cp.kd, cp.klines)
  const legendData = [...mainLegend(cp), ...subLegend(ind)]

  chart.setOption({
    backgroundColor: 'transparent',
    animation: false,
    legend: { data: legendData, textStyle: { color: '#8b90a0' }, top: 0 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1a1e2a', borderColor: '#2a2f3e', textStyle: { color: '#e6e8ee' },
    },
    grid: [
      { left: 60, right: 20, top: 30, height: '54%' },
      { left: 60, right: 20, top: '72%', height: '18%' },
    ],
    xAxis: [
      { type: 'category', data: cp.dates, gridIndex: 0, axisLine: { lineStyle: { color: '#2a2f3e' } }, axisLabel: { color: '#8b90a0' } },
      { type: 'category', data: cp.dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#2a2f3e' } } },
    ],
    yAxis: [
      { scale: true, gridIndex: 0, axisLabel: { color: '#8b90a0' }, splitLine: { lineStyle: { color: '#1f2430' } } },
      { scale: true, gridIndex: 1, axisLabel: { color: '#8b90a0' }, splitLine: { show: false } },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: cp.isCandle ? 60 : 0, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], top: '94%', height: 18, textStyle: { color: '#8b90a0' } },
    ],
    series: [...buildMainSeries(cp), ...sub],
  }, { replaceMerge: ['series'] })
}

// ---- 副图指标切换：只增量替换副图 series，主图零重建，毫秒级 ----
function switchIndicator(ind: 'vol' | 'macd' | 'kdj' | 'rsi') {
  if (ind === indicator.value) return
  indicator.value = ind
  if (!chart) return
  const cp = periodCache.get(period.value)
  if (!cp) return
  const sub = buildSubSeries(ind, cp.kd, cp.klines)
  const main = buildMainSeries(cp)
  // 用 replaceMerge 按 id 精确替换：保留主图（有 id 的不动），副图按 id 增删
  chart.setOption({
    series: [...main, ...sub],
    legend: { data: [...mainLegend(cp), ...subLegend(ind)] },
  }, { replaceMerge: ['series'] })
}

// ---- 周期切换：命中缓存则同步渲染（零网络），否则拉取后缓存 ----
async function switchPeriod(p: 'm5' | 'daily' | 'weekly' | 'monthly') {
  if (p === period.value) return
  period.value = p
  const cached = periodCache.get(p)
  if (cached) {
    // 命中缓存：同步渲染，毫秒级
    renderFull(cached, indicator.value)
    return
  }
  if (loadingPeriods.has(p)) return
  loadingPeriods.add(p)
  try {
    const cp = await fetchPeriod(p)
    periodCache.set(p, cp)
    if (period.value === p) renderFull(cp, indicator.value)
  } catch { /* 静默失败 */ } finally {
    loadingPeriods.delete(p)
  }
}

async function load() {
  if (!props.symbol) return
  // 换股票：清空缓存
  periodCache.clear()
  loadingPeriods.clear()
  try {
    const q = await getRealtimeQuote(props.symbol)
    quote.value = q || null
    await nextTick()
    const cp = await fetchPeriod(period.value)
    periodCache.set(period.value, cp)
    renderFull(cp, indicator.value)
  } catch { /* 静默失败 */ }
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
  periodCache.clear()
})

watch(() => props.symbol, () => load())
</script>

<style scoped>
.kline-wrap {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;
}
.quote-head { display: flex; align-items: baseline; flex-wrap: wrap; gap: 14px; margin-bottom: 12px; }
.q-name { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.q-symbol { font-size: 12px; color: var(--text-dim); font-weight: 400; }
.fav { font-size: 12px; cursor: pointer; color: var(--text-dim); font-weight: 400; transition: color 0.2s; user-select: none; }
.fav:hover { color: var(--gold); }
.fav.on { color: var(--gold); font-weight: 600; }
.q-price { font-size: 26px; font-weight: 800; }
.q-chg { font-size: 14px; font-weight: 600; }
.q-chg span { opacity: 0.7; margin-left: 6px; font-size: 12px; }
.q-meta { display: flex; gap: 14px; font-size: 12px; color: var(--text-dim); margin-left: auto; }
.q-meta b { font-weight: 600; }
.q-time { color: var(--text-dim); }
.up { color: var(--up); }
.down { color: var(--down); }
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.period-bar, .indicator-bar { display: flex; gap: 6px; }
.bar-btn {
  padding: 4px 12px; font-size: 12px; cursor: pointer; border-radius: 8px;
  color: var(--text-dim); border: 1px solid var(--border);
  transition: all 0.2s; user-select: none;
}
.bar-btn:hover { color: var(--text); border-color: var(--primary); }
.bar-btn.active {
  color: #fff; background: var(--primary); border-color: var(--primary);
  font-weight: 600;
}
.kline-chart { width: 100%; height: 420px; }
</style>
