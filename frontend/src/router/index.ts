import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/ocr',
      name: 'ocr',
      component: () => import('../views/OCR.vue')
    },
    {
      path: '/memos',
      name: 'memos',
      component: () => import('../views/Memos.vue')
    },
    {
      path: '/schedules',
      name: 'schedules',
      component: () => import('../views/Schedules.vue')
    }
  ]
})

export default router
