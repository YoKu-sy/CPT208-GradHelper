import { createRouter, createWebHistory } from 'vue-router'
import Intro from '../views/Intro.vue'
import AppInterface from '../views/AppInterface.vue'
import GpaCalculator from '../views/GpaCalculator.vue'
import IeltsAssistant from '../views/IeltsAssistant.vue'

const routes = [
  {
    path: '/',
    name: 'Intro',
    component: Intro,
    meta: { title: 'GradHelper - CPT208 Project' }
  },
  {
    path: '/app',
    name: 'AppInterface',
    component: AppInterface,
    meta: { title: 'GradHelper Hub' }
  },
  {
    path: '/ielts',
    name: 'IeltsAssistant',
    component: IeltsAssistant,
    meta: { title: 'IELTS Preparation Assistant' }
  },
  {
    path: '/gpa',
    name: 'GpaCalculator',
    component: GpaCalculator,
    meta: { title: 'GPA Conversion' }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: () => import('../views/KnowledgeBase.vue'),
    meta: { title: 'University Database' }
  },
  {
    path: '/detail/:type/:id',
    name: 'DetailView',
    component: () => import('../views/DetailView.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
