<script setup lang="ts">
/**
 * M01 数据大屏（监控驾驶舱）
 * [DEMO-ONLY] 使用 Mock 数据 + setInterval 模拟实时推送
 * 布局：顶部标题栏 + 左中右三栏
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import { mockBasinTree, mockAlerts, generateMockReading, mockStations } from '@/mock/station'
import type { AlertEvent, SensorReading } from '@/types/station'

import HeaderBar from './components/HeaderBar.vue'
import StationTree from './components/StationTree.vue'
import MapPanel from './components/MapPanel.vue'
import WaterLevelChart from './components/WaterLevelChart.vue'
import AlertList from './components/AlertList.vue'
import StatCards from './components/StatCards.vue'
import AgentChat from './components/AgentChat.vue'

const router = useRouter()
const authStore = useAuthStore()

// 当前选中站点
const selectedStationId = ref('stn-001')

// 实时统计指标
const stats = ref({
  currentWaterLevel: 24.35,
  rainfall1h: 12.5,
  currentFlow: 3200,
  alertCount: 3
})

// 预警列表
const alerts = ref<AlertEvent[]>([...mockAlerts])

// 实时数据更新定时器
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // [DEMO-ONLY] 每 3 秒更新一次数据，模拟 WebSocket 推送
  timer = setInterval(() => {
    const reading = generateMockReading(selectedStationId.value)
    stats.value = {
      currentWaterLevel: reading.waterLevel,
      rainfall1h: reading.rainfall,
      currentFlow: reading.flow,
      alertCount: alerts.value.filter(a => a.level !== 'BLUE').length
    }
  }, 3000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function handleStationSelect(stationId: string) {
  selectedStationId.value = stationId
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function goToDetail() {
  router.push('/detail')
}

function goToAdmin() {
  router.push('/admin')
}
</script>

<template>
  <div class="dashboard-container">
    <!-- 顶部标题栏 -->
    <HeaderBar
      :user="authStore.user"
      @logout="handleLogout"
      @go-detail="goToDetail"
      @go-admin="goToAdmin"
    />

    <!-- 主要内容区 -->
    <div class="dashboard-body">
      <!-- 左栏：站点树 -->
      <div class="panel-left">
        <StationTree
          :tree-data="mockBasinTree"
          :selected-id="selectedStationId"
          @select="handleStationSelect"
        />
      </div>

      <!-- 中栏：地图 + 指标卡 -->
      <div class="panel-center">
        <StatCards :stats="stats" />
        <MapPanel
          :stations="mockStations"
          :selected-id="selectedStationId"
          @select="handleStationSelect"
        />
      </div>

      <!-- 右栏：智能体 + 图表 + 预警 -->
      <div class="panel-right">
        <div class="right-agent">
          <AgentChat />
        </div>
        <div class="right-chart">
          <WaterLevelChart :station-id="selectedStationId" />
        </div>
        <div class="right-alerts">
          <AlertList :alerts="alerts" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  width: 100vw;
  height: 100vh;
  min-width: 1280px;
  min-height: 720px;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dashboard-body {
  flex: 1;
  display: flex;
  gap: 8px;
  padding: 8px;
  overflow: hidden;
  min-height: 0;
}

.panel-left {
  width: 260px;
  flex-shrink: 0;
  min-height: 0;
}

.panel-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

.panel-right {
  width: 420px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

.right-chart {
  flex: 2;
  min-height: 0;
  overflow: hidden;
}

.right-alerts {
  flex: 2;
  min-height: 0;
  overflow: hidden;
}

.right-agent {
  flex: 5;
  min-height: 0;
  overflow: hidden;
}
</style>
