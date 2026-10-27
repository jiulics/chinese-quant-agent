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
</style>
