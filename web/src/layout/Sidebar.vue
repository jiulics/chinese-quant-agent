<template>
  <aside class="sidebar">
    <div class="logo">
      <el-icon size="26" color="#409eff"><TrendCharts /></el-icon>
      <span class="logo-text">QuantAgent</span>
    </div>
    <div class="logo-sub">中文金融多智能体</div>

    <nav class="nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: route.path.startsWith(item.path) }"
      >
        <el-icon size="18"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="status-dot"></div>
      <span>v0.2.0 · 全功能版</span>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/research', label: '单股研究', icon: 'DataAnalysis' },
  { path: '/general', label: '通用研究', icon: 'Document' },
  { path: '/screener', label: '股票筛选', icon: 'Filter' },
  { path: '/picker', label: '选股助手', icon: 'Aim' },
  { path: '/assistant', label: '智能助手', icon: 'ChatDotRound' },
  { path: '/memory', label: 'AI 记忆', icon: 'Collection' },
  { path: '/skills', label: 'Skill 中心', icon: 'MagicStick' },
  { path: '/trading', label: '模拟交易', icon: 'Wallet' },
]
</script>

<style scoped>
.sidebar {
  width: 220px; flex-shrink: 0;
  background: var(--bg-soft); border-right: 1px solid var(--border);
  display: flex; flex-direction: column; padding: 20px 12px;
}
.logo { display: flex; align-items: center; gap: 10px; padding: 0 10px; }
.logo-text {
  font-size: 20px; font-weight: 700; letter-spacing: 0.5px;
  background: linear-gradient(90deg, #409eff, #7c5cff);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.logo-sub { font-size: 12px; color: var(--text-dim); padding: 2px 10px 14px; }
.nav { display: flex; flex-direction: column; gap: 3px; flex: 1; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: 10px;
  color: var(--text-dim); text-decoration: none; font-size: 14px;
  transition: all 0.2s;
}
.nav-item:hover { color: var(--text); background: var(--card); }
.nav-item.active {
  color: #fff;
  background: linear-gradient(90deg, rgba(64,158,255,0.2), rgba(124,92,255,0.15));
  border: 1px solid rgba(64,158,255,0.3);
}
.sidebar-footer {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; font-size: 12px; color: var(--text-dim);
  border-top: 1px solid var(--border);
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--down); box-shadow: 0 0 6px var(--down);
}
</style>
