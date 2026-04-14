import { createRouter, createWebHistory } from 'vue-router'
import Intro from '../views/Intro.vue'
import AppInterface from '../views/AppInterface.vue'
import AIChat from '../views/AIChat.vue'

const routes = [
  {
    path: '/',
    name: 'Intro',
    component: Intro,
    // 可以在这里加上网页标题的元数据
    meta: { title: 'GradHelper AI - CPT208 Project' }
  },
  {
    path: '/app',
    name: 'AppInterface',
    component: AppInterface,
    meta: { title: 'AI 升学助手' }
  },
  {
    // <--- 新增这段配置
    path: '/chat',
    name: 'AIChat',
    component: AIChat,
    meta: { title: 'AI Assistant Workbench' }
  }
]

const router = createRouter({
  // 使用 HTML5 的 history 模式，网址会很干净（没有 # 号）
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 每次切换路由时，页面自动回到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {23
      return { top: 0 }
    }
  }
})

// 可选：动态修改网页标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router