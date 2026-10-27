import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/research',
    },
    {
      path: '/research',
      name: 'research',
      component: () => import('../views/ResearchView.vue'),
      meta: { title: '单股研究' },
    },
    {
      path: '/screener',
      name: 'screener',
      component: () => import('../views/ScreenerView.vue'),
      meta: { title: '股票筛选' },
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: () => import('../views/AssistantView.vue'),
      meta: { title: '智能助手' },
    },
    {
      path: '/trading',
      name: 'trading',
      component: () => import('../views/TradingView.vue'),
      meta: { title: '模拟交易' },
    },
  ],
})

router.afterEach((to) => {
  document.title = (to.meta.title as string)
    ? `${to.meta.title} · chinese-quant-agent`
    : 'chinese-quant-agent'
})

export default router
