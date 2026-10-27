<template>
  <div class="view">
    <div class="page-head">
      <h1>AI 记忆</h1>
      <p>项目级记忆与事实沉淀，跨会话复用关键事实</p>
    </div>

    <div class="stats">
      <div class="stat-card"><div class="num">{{ stats.facts }}</div><div class="lbl">事实条目</div></div>
      <div class="stat-card"><div class="num">{{ stats.sessions }}</div><div class="lbl">会话记忆</div></div>
      <div class="stat-card"><div class="num">{{ stats.conversations }}</div><div class="lbl">对话历史</div></div>
    </div>

    <div class="input-row">
      <el-input v-model="newFact" placeholder="手动沉淀一条事实，例如：贵州茅台 2024 年 ROE 约 35%" size="large" @keyup.enter="add" />
      <el-button type="primary" size="large" @click="add">保存事实</el-button>
    </div>

    <el-input v-model="search" placeholder="搜索事实…" clearable @input="load" class="search" />

    <el-timeline v-if="facts.length" class="timeline">
      <el-timeline-item v-for="f in facts" :key="f.id" :timestamp="formatTime(f.created_at)">
        <div class="fact">
          <span>{{ f.content }}</span>
          <el-tag v-for="t in f.tags" :key="t" size="small" class="tag">{{ t }}</el-tag>
          <el-button size="small" text type="danger" @click="remove(f.id)">删除</el-button>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listFacts, addFact, deleteFact, memoryStats } from '@/api'
import { ElMessage } from 'element-plus'

const facts = ref<any[]>([])
const stats = ref({ facts: 0, sessions: 0, conversations: 0 })
const newFact = ref('')
const search = ref('')

async function load() {
  facts.value = await listFacts(search.value || undefined)
  stats.value = await memoryStats()
}

async function add() {
  if (!newFact.value.trim()) return
  await addFact(newFact.value.trim())
  newFact.value = ''
  ElMessage.success('已保存')
  load()
}

async function remove(id: string) {
  await deleteFact(id)
  load()
}

function formatTime(ts: number) {
  return new Date(ts * 1000).toLocaleString()
}

onMounted(load)
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.stats { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; text-align: center; }
.num { font-size: 32px; font-weight: 700; color: var(--primary); }
.lbl { color: var(--text-dim); font-size: 13px; margin-top: 4px; }
.input-row { display: flex; gap: 12px; margin-bottom: 16px; }
.search { margin-bottom: 20px; }
.timeline { padding-left: 4px; }
.fact { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.tag { margin-left: 4px; }
</style>
