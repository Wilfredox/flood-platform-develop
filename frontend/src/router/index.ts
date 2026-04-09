import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/river1d',
    name: 'river1d',
    component: () => import('@/views/river1d/River1DPage.vue'),
    meta: { requiresAuth: true, title: 'River1D 建模' }
  },
  {
    path: '/river1d/muskingum',
    name: 'river1d-muskingum',
    component: () => import('@/views/river1d/MuskingumPage.vue'),
    meta: { requiresAuth: true, title: '分段马斯金根' }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true, title: '数据大屏' }
  },
  {
    path: '/detail',
    name: 'detail',
    component: () => import('@/views/detail/DetailPage.vue'),
    meta: { requiresAuth: true, title: '实时详情' }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'province'] },
    children: [
      {
        path: '',
        redirect: '/admin/stations'
      },
      {
        path: 'stations',
        name: 'admin-stations',
        component: () => import('@/views/admin/StationManage.vue'),
        meta: { title: '站点管理' }
      },
      {
        path: 'alerts',
        name: 'admin-alerts',
        component: () => import('@/views/admin/AlertRuleConfig.vue'),
        meta: { title: '预警规则' }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'logs',
        name: 'admin-logs',
        component: () => import('@/views/admin/SystemLogs.vue'),
        meta: { title: '系统日志' }
      }
    ]
  },
  {
    path: '/',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录跳转登录页
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
