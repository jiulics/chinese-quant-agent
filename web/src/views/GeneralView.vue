<template>
  <div class="view">
    <div class="page-head">
      <h1>通用研究</h1>
      <p>自然语言研究任意市场主题：行业、板块、宏观、个股对比</p>
    </div>

    <div class="input-row">
      <el-input
        v-model="topic"
        placeholder="例如：分析新能源汽车行业 2025 年的投资机会"
        size="large"
        @keyup.enter="run"
      />
      <el-button type="primary" size="large" :loading="loading" @click="run">开始研究</el-button>
    </div>

    <el-card v-if="content" class="result-card" shadow="never">
      <template #header><span class="card-title">研究报告</span></template>
      <pre class="content">{{ content }}</pre>
    </el-card>

    <div v-if="!content && !loading" class="empty">
      <el-icon size="56" color="#3a4050"><Document /></el-icon>
      <p>输入研究主题，开始多维度研究</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { generalResearch } from '@/api'
import { ElMessage } from 'element-plus'

const topic = ref('')
const content = ref('')
const loading = ref(false)

async function run() {
  if (!topic.value.trim()) return
  loading.value = true
  content.value = ''
  try {
    const r = await generalResearch(topic.value.trim())
    content.value = r.content
  } catch (e: any) {
    ElMessage.error(e?.message || '研究失败')
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
.result-card { background: var(--card); border: 1px solid var(--border); }
.card-title { font-weight: 600; }
.content { white-space: pre-wrap; line-height: 1.8; font-size: 14px; color: var(--text); font-family: inherit; }
.empty { text-align: center; padding: 80px 0; color: var(--text-dim); }
.empty p { margin-top: 16px; }
</style>
