<script setup lang="ts">
/**
 * 预警列表滚动组件
 * 展示最近的预警事件，按等级颜色标记
 */
import type { AlertEvent } from '@/types/station'

defineProps<{
  alerts: AlertEvent[]
}>()

function alertColor(level: string): string {
  switch (level) {
    case 'RED': return '#F5222D'
    case 'ORANGE': return '#FA8C16'
    case 'YELLOW': return '#FAAD14'
    case 'BLUE': return '#1890FF'
    default: return '#8BA3C7'
  }
}

function alertLabel(level: string): string {
  switch (level) {
    case 'RED': return '红色·紧急'
    case 'ORANGE': return '橙色·警告'
    case 'YELLOW': return '黄色·预警'
    case 'BLUE': return '蓝色·关注'
    default: return '正常'
  }
}

function formatTime(ts: string): string {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="alert-list card-panel">
    <div class="card-title">🚨 实时预警</div>
    <div class="alerts-scroll">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="alert-item"
        :style="{ borderLeftColor: alertColor(alert.level) }"
      >
        <div class="alert-header">
          <span
            class="alert-badge"
            :style="{ background: alertColor(alert.level) + '22', color: alertColor(alert.level) }"
          >
            {{ alertLabel(alert.level) }}
          </span>
          <span class="alert-time">{{ formatTime(alert.timestamp) }}</span>
        </div>
        <div class="alert-station">{{ alert.stationName }}</div>
        <div class="alert-message">{{ alert.message }}</div>
        <div class="alert-detail">
          {{ alert.metric }}：{{ alert.value }}（阈值：{{ alert.threshold }}）
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.alert-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.alerts-scroll {
  flex: 1;
  overflow-y: auto;
  padding-top: 8px;
}

.alert-item {
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(13, 27, 42, 0.5);
  border-left: 3px solid;
  border-radius: 0 6px 6px 0;
  transition: background 0.2s;
}

.alert-item:hover {
  background: var(--bg-tertiary);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.alert-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}

.alert-time {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: var(--font-family-number);
}

.alert-station {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 2px;
}

.alert-message {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.alert-detail {
  font-size: 11px;
  color: var(--text-tertiary);
}
</style>
