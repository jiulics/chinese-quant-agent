<template>
  <el-config-provider :locale="zhCn">
    <div class="app-shell">
      <Sidebar />
      <main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import Sidebar from '@/layout/Sidebar.vue'
</script>

<style>
:root {
  --bg: #0f1117;
  --bg-soft: #171a23;
  --card: #1a1e2a;
  --card-hover: #20263a;
  --border: #2a2f3e;
  --text: #e6e8ee;
  --text-dim: #8b90a0;
  --primary: #409eff;
  --up: #f56c6c;
  --down: #67c23a;
  --gold: #e6a23c;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app {
  height: 100%; background: var(--bg); color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
}
.app-shell { display: flex; height: 100vh; overflow: hidden; }
.main { flex: 1; overflow-y: auto; padding: 24px 28px; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ===== Element Plus 暗色主题覆盖 ===== */
.el-input__wrapper, .el-select__wrapper, .el-textarea__inner,
.el-input__inner, .el-input-number {
  background: var(--bg-soft) !important;
  box-shadow: 0 0 0 1px var(--border) inset !important;
}
.el-input__wrapper.is-focus, .el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px var(--primary) inset !important;
}
.el-select-dropdown, .el-popper, .el-picker-panel {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
}
.el-select-dropdown__item { color: var(--text) !important; }
.el-select-dropdown__item.is-hovering, .el-select-dropdown__item:hover {
  background: var(--card-hover) !important;
}
.el-select-dropdown__item.is-selected { color: var(--primary) !important; }
.el-radio-button__inner {
  background: var(--bg-soft) !important; color: var(--text-dim) !important;
  border-color: var(--border) !important;
}
.el-radio-button__original-radio:checked + .el-radio-button__inner {
  background: var(--primary) !important; color: #fff !important;
  border-color: var(--primary) !important;
}
.el-switch.is-checked .el-switch__core { background: var(--primary) !important; border-color: var(--primary) !important; }
.el-card, .el-dialog, .el-drawer { background: var(--card) !important; border-color: var(--border) !important; }
.el-table, .el-table tr, .el-table th, .el-table td { background: transparent !important; color: var(--text) !important; }
.el-table th { color: var(--text-dim) !important; }
.el-table--border::after, .el-table--group::after { background: var(--border) !important; }
.el-tag { background: var(--bg-soft) !important; border-color: var(--border) !important; color: var(--text-dim) !important; }
.el-alert--error { background: rgba(245,108,108,0.1) !important; border-color: rgba(245,108,108,0.3) !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #2a2f3e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3a4050; }
::-webkit-scrollbar-track { background: transparent; }
</style>
