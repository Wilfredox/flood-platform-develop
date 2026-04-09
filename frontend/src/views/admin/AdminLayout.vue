<script setup lang="ts">
/**
 * M03 后台管理系统 · 主布局
 * Element Plus Container 布局：侧边栏 + 顶部导航 + 内容区
 */
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isCollapse = ref(false)

const menuItems = computed(() => {
  const all = [
    { index: '/admin/stations', icon: 'Location', label: '站点管理', name: 'admin-stations' },
    { index: '/admin/alerts', icon: 'Bell', label: '预警规则', name: 'admin-alerts' },
    { index: '/admin/users', icon: 'User', label: '用户管理', name: 'admin-users' },
    { index: '/admin/logs', icon: 'Document', label: '系统日志', name: 'admin-logs' }
  ]
  return all.filter(item => authStore.hasMenu(item.name))
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="admin-sidebar" :class="{ collapsed: isCollapse }">
      <div class="sidebar-header">
        <span class="sidebar-logo">🌊</span>
        <span v-if="!isCollapse" class="sidebar-title">管理后台</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="admin-menu"
      >
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button text @click="isCollapse = !isCollapse" style="color: var(--text-tertiary);">
          {{ isCollapse ? '»' : '«' }}
        </el-button>
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="admin-main">
      <!-- 顶部导航 -->
      <div class="admin-header">
        <div class="header-breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>后台管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-actions">
          <el-button text @click="router.push('/dashboard')" style="color: var(--text-secondary);">← 返回大屏</el-button>
          <span class="user-tag">{{ authStore.user?.name }} ({{ authStore.currentRole }})</span>
          <el-button text @click="handleLogout" style="color: var(--text-tertiary);">退出</el-button>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  width: 100%;
  height: 100vh;
  display: flex;
  background: var(--bg-primary);
  overflow: hidden;
}

.admin-sidebar {
  width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  flex-shrink: 0;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-logo {
  font-size: 24px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.admin-menu {
  flex: 1;
  border-right: none !important;
}

:deep(.el-menu) {
  background-color: transparent !important;
}

.sidebar-footer {
  padding: 8px;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  height: 52px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-tag {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 3px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.admin-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

:deep(.el-breadcrumb__inner) {
  color: var(--text-tertiary) !important;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-secondary) !important;
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-tertiary) !important;
}
</style>
