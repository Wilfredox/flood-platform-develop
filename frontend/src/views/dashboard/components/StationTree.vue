<script setup lang="ts">
/**
 * 流域站点树形列表（浙江省版）
 * 浙江省目录下包含南江流域，南江流域站点高亮显示
 */
import { ref } from 'vue'
import type { BasinTree } from '@/types/station'

defineProps<{
  treeData: BasinTree[]
  selectedId: string
}>()

const emit = defineEmits<{
  (e: 'select', stationId: string): void
}>()

// 默认展开南江流域
const expandedBasins = ref<Set<string>>(new Set(['basin-nanjiang']))

function toggleBasin(basinId: string) {
  if (expandedBasins.value.has(basinId)) {
    expandedBasins.value.delete(basinId)
  } else {
    expandedBasins.value.add(basinId)
  }
}

function statusIcon(status: string) {
  switch (status) {
    case 'online':  return '🟢'
    case 'warning': return '🟡'
    case 'offline': return '🔴'
    default:        return '⚪'
  }
}

function isNanjiang(basinId: string) {
  return basinId === 'basin-nanjiang'
}
</script>

<template>
  <div class="station-tree card-panel">
    <div class="card-title">
      <span>📍 浙江省流域站点</span>
      <span class="province-tag">浙江省</span>
    </div>

    <div class="tree-content">
      <div
        v-for="basin in treeData"
        :key="basin.id"
        class="basin-group"
        :class="{ 'basin-group--nanjiang': isNanjiang(basin.id) }"
      >
        <!-- 流域标题（可折叠） -->
        <div
          class="basin-header"
          :class="{ 'basin-header--nanjiang': isNanjiang(basin.id) }"
          @click="toggleBasin(basin.id)"
        >
          <span class="basin-expand">
            {{ expandedBasins.has(basin.id) ? '▾' : '▸' }}
          </span>
          <span class="basin-icon">
            {{ isNanjiang(basin.id) ? '🌊' : '🏞' }}
          </span>
          <span class="basin-name">{{ basin.label }}</span>
          <span class="basin-count">{{ basin.children.length }}</span>
        </div>

        <!-- 站点列表（折叠控制） -->
        <div v-if="expandedBasins.has(basin.id)" class="basin-children">
          <div
            v-for="stn in basin.children"
            :key="stn.id"
            class="station-item"
            :class="{
              active: stn.id === selectedId,
              'station-item--nanjiang': isNanjiang(basin.id)
            }"
            @click="emit('select', stn.id)"
          >
            <span class="stn-status">{{ statusIcon(stn.status) }}</span>
            <span class="stn-name">{{ stn.label }}</span>
            <span
              v-if="isNanjiang(basin.id)"
              class="stn-badge"
              title="南江流域核心站"
            >核</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.station-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.province-tag {
  font-size: 10px;
  color: #00D4FF;
  background: rgba(0, 212, 255, 0.12);
  border: 1px solid rgba(0, 212, 255, 0.3);
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 600;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding-top: 6px;
}

.basin-group {
  margin-bottom: 4px;
}

/* 南江流域组容器 */
.basin-group--nanjiang {
  background: rgba(82, 196, 26, 0.04);
  border-radius: 8px;
  border: 1px solid rgba(82, 196, 26, 0.18);
  margin-bottom: 10px;
  overflow: hidden;
}

/* 流域标题行 */
.basin-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  cursor: pointer;
  user-select: none;
  border-radius: 6px;
  transition: background 0.15s;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-accent);
}

.basin-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* 南江流域标题 */
.basin-header--nanjiang {
  color: #52C41A;
  padding: 8px 10px;
  background: rgba(82, 196, 26, 0.08);
}

.basin-header--nanjiang:hover {
  background: rgba(82, 196, 26, 0.15);
}

.basin-expand {
  font-size: 10px;
  color: var(--text-tertiary);
  flex-shrink: 0;
  width: 10px;
}

.basin-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.basin-name {
  flex: 1;
}

.basin-count {
  font-size: 11px;
  color: var(--text-tertiary);
  background: var(--bg-tertiary);
  padding: 1px 6px;
  border-radius: 8px;
  font-weight: 400;
}

/* 站点列表区 */
.basin-children {
  padding-bottom: 4px;
}

/* 站点行 */
.station-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px 7px 28px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.18s;
  font-size: 13px;
  color: var(--text-secondary);
}

.station-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.station-item.active {
  background: rgba(24, 144, 255, 0.15);
  color: var(--color-primary);
  border-left: 3px solid var(--color-primary);
  padding-left: 25px;
}

/* 南江流域站点 hover/active 颜色 */
.station-item--nanjiang:hover {
  background: rgba(82, 196, 26, 0.1);
  color: #73D13D;
}

.station-item--nanjiang.active {
  background: rgba(82, 196, 26, 0.15);
  color: #52C41A;
  border-left-color: #52C41A;
}

.stn-status {
  font-size: 9px;
  flex-shrink: 0;
}

.stn-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 南江流域核心站徽标 */
.stn-badge {
  font-size: 9px;
  font-weight: 700;
  color: #52C41A;
  background: rgba(82, 196, 26, 0.15);
  border: 1px solid rgba(82, 196, 26, 0.35);
  padding: 1px 4px;
  border-radius: 3px;
  flex-shrink: 0;
}
</style>
