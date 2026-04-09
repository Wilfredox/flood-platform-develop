<script setup lang="ts">
/**
 * 顶部关键指标卡片
 */
defineProps<{
  stats: {
    currentWaterLevel: number
    rainfall1h: number
    currentFlow: number
    alertCount: number
  }
}>()

// 水位状态色
function waterLevelColor(val: number): string {
  if (val >= 28) return 'var(--alert-red)'
  if (val >= 26.5) return 'var(--alert-orange)'
  if (val >= 25) return 'var(--alert-yellow)'
  return 'var(--color-accent)'
}
</script>

<template>
  <div class="stat-cards">
    <div class="stat-card">
      <div class="stat-label">当前水位</div>
      <div class="stat-value" :style="{ color: waterLevelColor(stats.currentWaterLevel) }">
        {{ stats.currentWaterLevel.toFixed(2) }}
        <span class="stat-unit">m</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">1h 雨量</div>
      <div class="stat-value" style="color: var(--color-primary);">
        {{ stats.rainfall1h.toFixed(1) }}
        <span class="stat-unit">mm</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">实时流量</div>
      <div class="stat-value" style="color: var(--color-accent);">
        {{ stats.currentFlow }}
        <span class="stat-unit">m³/s</span>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-label">活跃预警</div>
      <div class="stat-value" :style="{ color: stats.alertCount > 2 ? 'var(--alert-red)' : 'var(--color-warning)' }">
        {{ stats.alertCount }}
        <span class="stat-unit">条</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-cards {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.stat-card {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 12px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
}

.stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-family-number);
  letter-spacing: 1px;
}

.stat-unit {
  font-size: 14px;
  font-weight: 400;
  margin-left: 4px;
  opacity: 0.7;
}
</style>
