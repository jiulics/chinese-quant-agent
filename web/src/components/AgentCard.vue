<template>
  <div class="agent-card" :class="{ 'agent-done': agent.done }">
    <div class="agent-head">
      <span class="agent-dot" :class="{ done: agent.done }"></span>
      <span class="agent-label">{{ agent.label }}</span>
      <el-icon v-if="!agent.done" class="agent-spin"><Loading /></el-icon>
      <el-icon v-else class="agent-check"><CircleCheck /></el-icon>
    </div>
    <div class="agent-body">
      <pre class="agent-text">{{ agent.content || '等待分析…' }}</pre>
      <span v-if="!agent.done && agent.content" class="cursor">▌</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgentProgress } from '@/stores/analysis'

defineProps<{ agent: AgentProgress }>()
</script>

<style scoped>
.agent-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; overflow: hidden; transition: border-color 0.3s;
}
.agent-card.agent-done { border-color: rgba(103,194,58,0.4); }
.agent-head {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-bottom: 1px solid var(--border);
  background: var(--bg-soft);
}
.agent-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--gold); }
.agent-dot.done { background: var(--down); }
.agent-label { font-weight: 600; font-size: 13px; }
.agent-spin { margin-left: auto; color: var(--primary); animation: spin 1s linear infinite; }
.agent-check { margin-left: auto; color: var(--down); }
.agent-body { padding: 16px; position: relative; }
.agent-text { white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.7; color: var(--text); font-family: inherit; }
.cursor { color: var(--primary); animation: blink 1s step-end infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes blink { 50% { opacity: 0; } }
</style>
