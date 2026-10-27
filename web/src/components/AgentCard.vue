<template>
  <div class="agent-card" :class="{ 'is-active': agent.active, 'is-done': agent.done }">
    <div class="agent-head" @click="toggle">
      <div class="head-left">
        <span class="order-badge">{{ agent.order + 1 }}</span>
        <span class="agent-dot" :class="{ done: agent.done, active: agent.active }"></span>
        <span class="agent-label">{{ agent.label }}</span>
        <el-icon v-if="agent.active" class="agent-spin"><Loading /></el-icon>
        <el-icon v-else-if="agent.done" class="agent-check"><CircleCheck /></el-icon>
        <el-icon v-else class="agent-wait"><Clock /></el-icon>
      </div>
      <div class="head-right">
        <span v-if="agent.active" class="status-tag streaming">分析中</span>
        <span v-else-if="agent.done" class="status-tag done">已完成</span>
        <span v-else class="status-tag pending">待开始</span>
        <el-icon class="chevron" :class="{ open: expanded }"><ArrowDown /></el-icon>
      </div>
    </div>

    <transition name="collapse">
      <div v-show="expanded" class="agent-body">
        <pre class="agent-text">{{ agent.content || '等待分析…' }}</pre>
        <span v-if="agent.active" class="cursor">▌</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AgentProgress } from '@/stores/analysis'

const props = defineProps<{ agent: AgentProgress }>()

// 分析中自动展开；完成后由用户手动展开查看全文
const expanded = ref(false)

watch(
  () => props.agent.active,
  (active) => { if (active) expanded.value = true },
)

watch(
  () => props.agent.done,
  (done) => { if (done) expanded.value = false },
)

function toggle() {
  // 分析中不允许收起
  if (props.agent.active) return
  expanded.value = !expanded.value
}
</script>

<style scoped>
.agent-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; transition: all 0.25s;
}
.agent-card.is-active { border-color: rgba(64,158,255,0.6); box-shadow: 0 0 0 1px rgba(64,158,255,0.25); }
.agent-card.is-done { border-color: rgba(103,194,58,0.35); }
.agent-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; cursor: pointer; user-select: none;
  background: var(--bg-soft); transition: background 0.2s;
}
.agent-head:hover { background: rgba(64,158,255,0.06); }
.head-left { display: flex; align-items: center; gap: 10px; }
.head-right { display: flex; align-items: center; gap: 10px; }
.order-badge {
  width: 22px; height: 22px; border-radius: 6px; font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  background: rgba(64,158,255,0.12); color: var(--primary);
}
.agent-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-dim); }
.agent-dot.done { background: var(--down); }
.agent-dot.active { background: var(--primary); animation: pulse 1s ease-in-out infinite; }
.agent-label { font-weight: 600; font-size: 14px; }
.agent-spin { color: var(--primary); animation: spin 1s linear infinite; }
.agent-check { color: var(--down); }
.agent-wait { color: var(--text-dim); }
.status-tag { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.status-tag.streaming { background: rgba(64,158,255,0.15); color: var(--primary); }
.status-tag.done { background: rgba(103,194,58,0.15); color: var(--down); }
.status-tag.pending { background: rgba(58,64,80,0.4); color: var(--text-dim); }
.chevron { color: var(--text-dim); transition: transform 0.2s; }
.chevron.open { transform: rotate(180deg); }
.agent-body { padding: 16px 18px; position: relative; max-height: 420px; overflow-y: auto; }
.agent-text {
  white-space: pre-wrap; word-break: break-word; font-size: 13px;
  line-height: 1.75; color: var(--text); font-family: inherit; margin: 0;
}
.cursor { color: var(--primary); animation: blink 1s step-end infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes blink { 50% { opacity: 0; } }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
.collapse-enter-active, .collapse-leave-active { transition: all 0.25s; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; }
</style>
