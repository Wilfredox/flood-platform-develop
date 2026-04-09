<script setup lang="ts">
/**
 * 大屏顶部标题栏组件
 */
import type { UserInfo } from '@/types/common'

defineProps<{
  user: UserInfo | null
}>()

const emit = defineEmits<{
  (e: 'logout'): void
  (e: 'goDetail'): void
  (e: 'goAdmin'): void
}>()

function notAvailable(name: string) {
  window.alert?.(`「${name}」功能尚在开发中，当前为占位入口，敬请期待。`)
}
</script>

<template>
  <div class="header-bar">
    <div class="header-left">
      <img src="@/assets/logo.svg" alt="logo" class="header-logo" />
      <div class="header-titles">
        <span class="header-title">澜镜数字孪生洪水预警监管平台</span>
        <span class="header-subtitle">LanJing Digital Twin Flood Warning Platform</span>
      </div>
    </div>
    <div class="header-center">
      <span class="header-time">{{ new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }) }}</span>
    </div>
    <div class="header-right">
      <el-button text class="nav-btn" @click="emit('goDetail')">  实时详情</el-button>
      <el-button text class="nav-btn" @click="$router.push('/river1d')">River1D</el-button>
      <el-button text class="nav-btn" @click="notAvailable('历史回溯')">历史回溯</el-button>
      <el-button text class="nav-btn" @click="notAvailable('数字孪生')">数字孪生</el-button>
      <el-button text class="nav-btn" @click="notAvailable('应急指挥')">应急指挥</el-button>
      <el-button text class="nav-btn" @click="emit('goAdmin')">  系统管理</el-button>
      <span class="nav-divider">|</span>
      <span class="user-info" v-if="user">
        {{ user.name }} ({{ user.role }})
      </span>
      <el-button text class="logout-btn" @click="emit('logout')">退出</el-button>
    </div>
  </div>
</template>

<style scoped>
.header-bar {
  height: 52px;
  background: linear-gradient(180deg, rgba(13, 27, 42, 0.95) 0%, rgba(27, 40, 56, 0.9) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-titles {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
}

.header-logo {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(90deg, #E8F0FE, #00D4FF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}

.header-subtitle {
  font-size: 11px;
  color: var(--text-tertiary);
  line-height: 1.2;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.header-time {
  font-size: 14px;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-btn {
  color: var(--text-secondary) !important;
  font-size: 12px;
  padding: 4px 8px;
}

.nav-btn:hover {
  color: var(--color-accent) !important;
}

.nav-divider {
  color: var(--border-color);
  font-size: 12px;
  margin: 0 2px;
}

.user-info {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 4px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.logout-btn {
  color: var(--text-tertiary) !important;
  font-size: 12px;
}

.logout-btn:hover {
  color: var(--color-danger) !important;
}
</style>
