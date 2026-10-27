<template>
  <div class="ph">
    <div class="page-head"><h1>智能助手</h1><p>联网搜索 + 工具调用 + 事实记忆</p></div>
    <div class="ph-card">
      <el-icon size="48" color="#3a4050"><ChatDotRound /></el-icon>
      <p>该模块将在后续阶段实现</p>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.ph { max-width: 1100px; margin: 0 auto; }
.page-head h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.ph-card {
  text-align: center; padding: 80px 0; color: var(--text-dim);
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
}
.ph-card p { margin-top: 16px; }
</style>
