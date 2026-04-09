<script setup lang="ts">
/**
 * R1DToolbar.vue — River1D 顶部工具栏
 * M08: 绘制工具切换 / 撤销捕捉取消 / 全图 / 节点 / 拓扑 / 方案管理 / 导出
 */
import { computed } from 'vue'
import { useRiver1dStore } from '@/stores/useRiver1dStore'
import type { DrawTool } from '@/types/river1d'

const emit = defineEmits<{
  (e: 'fitAll'): void
  (e: 'cancelDraw'): void
  (e: 'genNodes'): void
  (e: 'checkTopo'): void
  (e: 'newProject'): void
  (e: 'openProject'): void
  (e: 'saveProject'): void
  (e: 'saveProjectAs'): void
  (e: 'exportData'): void
}>()

const store = useRiver1dStore()

const TOOLS: { key: DrawTool; label: string; color: string; title: string; icon: string }[] = [
  { key: 'select',    label: '选择',   color: '#6c63ff', title: '选择要素 [S]', icon: '/cursors/select.svg' },
  { key: 'river',     label: '河道',   color: '#1a6cff', title: '绘制河道中心线 [R]', icon: '/cursors/Riverway.svg' },
  { key: 'bank',      label: '岸线',   color: '#00a878', title: '绘制岸线/堤防 [B]', icon: '/cursors/water_front.svg' },
  { key: 'section',   label: '断面',   color: '#f4a261', title: '绘制横断面 [X]', icon: '/cursors/fracture_surface.svg' },
  { key: 'structure', label: '建筑物', color: '#e63946', title: '绘制水工建筑物 [W]', icon: '/cursors/construction.svg' },
  { key: 'node',      label: '节点',   color: '#00c2ff', title: '节点编辑（拖拽顶点改线）[N]', icon: '/cursors/node.svg' },
]

const isDrawing = computed(() => ['river', 'bank', 'section', 'structure'].includes(store.activeTool))
const snapBtnLabel = computed(() => store.snapEnabled ? '捕捉 ON' : '捕捉 OFF')
</script>

<template>
  <div class="r1d-toolbar">
    <!-- 工具组 1: 选择 + 绘制工具 -->
    <div class="tb-group tb-group-tools">
      <button
        v-for="tool in TOOLS"
        :key="tool.key"
        class="dt-btn"
        :class="{ active: store.activeTool === tool.key }"
        :style="store.activeTool === tool.key ? { background: tool.color } : {}"
        :title="tool.title"
        @click="store.setTool(tool.key)"
      >
        <img class="dt-icon" :src="tool.icon" :alt="tool.label" />
        {{ tool.label }}
      </button>
    </div>

    <div class="tb-sep" />

    <!-- 工具组 2: 编辑操作 -->
    <div class="tb-group">
      <button class="hb" title="撤销上一步 (Ctrl+Z)" @click="store.undoLast()">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M2 6L5 3M2 6L5 9M2 6H8C10.2 6 12 7.8 12 10"/>
        </svg>
        撤销
      </button>
      <button class="hb" :class="{ 'snap-on': store.snapEnabled }" title="切换节点捕捉" @click="store.toggleSnap()">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="6" cy="6" r="2.5"/><path d="M6 1V3.5M6 8.5V11M1 6H3.5M8.5 6H11"/>
        </svg>
        {{ snapBtnLabel }}
      </button>
      <button class="hb" :disabled="!isDrawing" title="取消当前绘制 (ESC)" @click="emit('cancelDraw')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M3 3L9 9M9 3L3 9"/>
        </svg>
        取消
      </button>
    </div>

    <div class="tb-sep" />

    <!-- 工具组 3: 地图视图 + 拓扑 -->
    <div class="tb-group">
      <button class="hb" title="缩放到全部要素" @click="emit('fitAll')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <rect x="1" y="1" width="4" height="4" rx=".5"/><rect x="7" y="1" width="4" height="4" rx=".5"/>
          <rect x="1" y="7" width="4" height="4" rx=".5"/><rect x="7" y="7" width="4" height="4" rx=".5"/>
        </svg>
        全图
      </button>
      <button class="hb" title="自动生成拓扑节点" @click="emit('genNodes')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="6" cy="3" r="1.5"/><circle cx="2" cy="9" r="1.5"/><circle cx="10" cy="9" r="1.5"/>
          <path d="M5.1 4.5L2.5 7.5M6.9 4.5L9.5 7.5"/>
        </svg>
        生成节点
      </button>
      <button class="hb" title="执行拓扑检查" @click="emit('checkTopo')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M2 7L4.5 9.5L10 4"/>
        </svg>
        拓扑
      </button>
    </div>

    <div class="tb-sep" />

    <!-- 工具组 4: 方案操作 -->
    <div class="tb-group">
      <button class="hb" title="新建方案 (Ctrl+N)" @click="emit('newProject')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M7 1H3C2.4 1 2 1.4 2 2V10C2 10.6 2.4 11 3 11H9C9.6 11 10 10.6 10 10V4L7 1Z"/>
          <path d="M7 1V4H10" opacity=".6"/><path d="M5 7H7.5M6.5 6V8" />
        </svg>
        新建
      </button>
      <button class="hb" title="打开方案文件 (.r1d)" @click="emit('openProject')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M1 4V10C1 10.6 1.4 11 2 11H10C10.6 11 10 10 10 9.5V5C10 4.4 9.6 4 9 4H5.5L4.5 2.5C4.2 2 3.8 2 3.5 2H2C1.4 2 1 2.4 1 3V4Z"/>
        </svg>
        打开
      </button>
      <button
        class="hb"
        :class="{ dirty: store.isDirty }"
        title="保存方案 (Ctrl+S)"
        @click="emit('saveProject')"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M2 1H8L11 4V11H2V1Z"/><path d="M4 1V4H8V1" opacity=".6"/>
          <rect x="3" y="7" width="6" height="4" rx=".5" opacity=".6"/>
        </svg>
        保存
      </button>
      <div class="tb-sep" />
      <button class="hb hb-teal" title="导出数据" @click="emit('exportData')">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M6 8V2M3.5 5.5L6 8L8.5 5.5"/><path d="M2 10H10"/>
        </svg>
        导出
      </button>
    </div>
  </div>
</template>

<style scoped>
.r1d-toolbar {
  height: 48px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 0;
  flex-shrink: 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.tb-group {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
}

.tb-group-tools {
  padding-left: 0;
}

.tb-sep {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  flex-shrink: 0;
}

/* 绘制工具按钮 */
.dt-btn {
  height: 28px;
  padding: 0 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,.06);
  color: var(--text-secondary);
  transition: all .15s;
  white-space: nowrap;
}
.dt-btn:hover { background: rgba(0,212,255,.14); color: var(--text-primary); }
.dt-btn.active { color: #fff; box-shadow: 0 0 0 2px rgba(255,255,255,.2); }

.dt-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
  flex-shrink: 0;
  filter: saturate(.15) brightness(1.45);
}

.dt-btn.active .dt-icon {
  filter: saturate(0) brightness(8);
}

/* 普通工具按钮 */
.hb {
  height: 28px;
  padding: 0 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,.08);
  color: var(--text-secondary);
  transition: all .15s;
  white-space: nowrap;
}
.hb:hover { background: rgba(0,212,255,.14); color: var(--text-primary); }
.hb:disabled { opacity: .35; cursor: not-allowed; }
.hb.snap-on { color: var(--color-accent); }
.hb.dirty { color: #f4a261; }
.hb-teal { background: #0a9396; color: #fff; }
.hb-teal:hover { background: #077880; }
</style>
