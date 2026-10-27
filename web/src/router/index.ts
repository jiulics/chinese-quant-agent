import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/research' },
    { path: '/research', name: 'research', component: () => import('../views/ResearchView.vue'), meta: { title: '单股研究' } },
    { path: '/general', name: 'general', component: () => import('../views/GeneralView.vue'), meta: { title: '通用研究' } },
    { path: '/screener', name: 'screener', component: () => import('../views/ScreenerView.vue'), meta: { title: '股票筛选' } },
    { path: '/picker', name: 'picker', component: () => import('../views/PickerView.vue'), meta: { title: '选股助手' } },
    { path: '/assistant', name: 'assistant', component: () => import('../views/AssistantView.vue'), meta: { title: '智能助手' } },
    { path: '/memory', name: 'memory', component: () => import('../views/MemoryView.vue'), meta: { title: 'AI 记忆' } },
    { path: '/skills', name: 'skills', component: () => import('../views/SkillsView.vue'), meta: { title: 'Skill 中心' } },
    { path: '/trading', name: 'trading', component: () => import('../views/TradingView.vue'), meta: { title: '模拟交易' } },
  ],
})

router.afterEach((to) => {
  document.title = (to.meta.title as string)
    ? `${to.meta.title} · chinese-quant-agent`
    : 'chinese-quant-agent'
})

export default router
