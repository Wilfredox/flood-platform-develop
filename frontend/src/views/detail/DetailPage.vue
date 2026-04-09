<script setup lang="ts">
/**
 * M02 实时详细数据页
 * [DEMO-ONLY] 三联图联动 + 帕累托散点图 + 数据明细表
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { mockStations, generateHistory24h } from '@/mock/station'
import { generateParetoSolutions } from '@/mock/optimization'
import type { SensorReading } from '@/types/station'
import type { ParetoSolution } from '@/types/common'

const router = useRouter()

// 站点选择
const selectedStation = ref('stn-001')
const stationOptions = mockStations.map(s => ({ value: s.id, label: s.name }))

// 时间范围快捷选项
const timeRange = ref('24h')
const timeOptions = [
  { value: '1h', label: '近 1 小时' },
  { value: '6h', label: '近 6 小时' },
  { value: '24h', label: '近 24 小时' },
  { value: '7d', label: '近 7 天' }
]

// 历史数据
const historyData = ref<SensorReading[]>([])
// 帕累托解集
const paretoSolutions = ref<ParetoSolution[]>([])
const selectedSolution = ref<ParetoSolution | null>(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return historyData.value.slice(start, start + pageSize.value)
})

// 图表容器
const tripleChartRef = ref<HTMLDivElement>()
const paretoChartRef = ref<HTMLDivElement>()
const scheduleChartRef = ref<HTMLDivElement>()
let tripleChart: echarts.ECharts | null = null
let paretoChart: echarts.ECharts | null = null
let scheduleChart: echarts.ECharts | null = null

function loadData() {
  historyData.value = generateHistory24h(selectedStation.value)
  paretoSolutions.value = generateParetoSolutions()
  selectedSolution.value = paretoSolutions.value.find(s => s.isRecommended) || null
  renderTripleChart()
  renderParetoChart()
  renderScheduleChart()
}

function renderTripleChart() {
  if (!tripleChartRef.value) return
  if (!tripleChart) tripleChart = echarts.init(tripleChartRef.value)

  const times = historyData.value.map(d => {
    const date = new Date(d.timestamp)
    return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
  })

  tripleChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13,27,42,0.9)',
      borderColor: '#2A3F55',
      textStyle: { color: '#E8F0FE', fontSize: 12 }
    },
    legend: {
      data: ['水位 (m)', '雨量 (mm/h)', '流量 (m³/s)'],
      textStyle: { color: '#8BA3C7', fontSize: 11 },
      top: 8
    },
    grid: [
      { left: 60, right: 60, top: 48, height: '22%' },
      { left: 60, right: 60, top: '40%', height: '22%' },
      { left: 60, right: 60, top: '72%', height: '22%' }
    ],
    xAxis: [
      { type: 'category', data: times, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#2A3F55' } } },
      { type: 'category', data: times, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#2A3F55' } } },
      { type: 'category', data: times, gridIndex: 2, axisLine: { lineStyle: { color: '#2A3F55' } }, axisLabel: { color: '#8BA3C7', fontSize: 10 } }
    ],
    yAxis: [
      { type: 'value', name: '水位(m)', gridIndex: 0, nameTextStyle: { color: '#8BA3C7' }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } },
      { type: 'value', name: '雨量(mm/h)', gridIndex: 1, nameTextStyle: { color: '#8BA3C7' }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } },
      { type: 'value', name: '流量(m³/s)', gridIndex: 2, nameTextStyle: { color: '#8BA3C7' }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } }
    ],
    series: [
      { name: '水位 (m)', type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: historyData.value.map(d => d.waterLevel), smooth: true, lineStyle: { color: '#00D4FF', width: 2 }, itemStyle: { color: '#00D4FF' }, areaStyle: { color: 'rgba(0,212,255,0.1)' } },
      { name: '雨量 (mm/h)', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: historyData.value.map(d => d.rainfall), itemStyle: { color: '#1890FF' }, barWidth: 6 },
      { name: '流量 (m³/s)', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: historyData.value.map(d => d.flow), smooth: true, lineStyle: { color: '#52C41A', width: 2 }, itemStyle: { color: '#52C41A' }, areaStyle: { color: 'rgba(82,196,26,0.1)' } }
    ]
  })
}

function renderParetoChart() {
  if (!paretoChartRef.value) return
  if (!paretoChart) paretoChart = echarts.init(paretoChartRef.value)

  const data = paretoSolutions.value.map(s => ({
    value: [s.floodBenefit, s.powerBenefit],
    name: s.id,
    itemStyle: {
      color: s.isRecommended ? '#F5222D' : '#1890FF',
      borderColor: s.isRecommended ? '#fff' : 'transparent',
      borderWidth: s.isRecommended ? 2 : 0
    },
    symbolSize: s.isRecommended ? 16 : 10
  }))

  paretoChart.setOption({
    backgroundColor: 'transparent',
    title: { text: '帕累托前沿 · 防洪 vs 发电', textStyle: { color: '#E8F0FE', fontSize: 14 }, left: 8, top: 4 },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(13,27,42,0.9)',
      borderColor: '#2A3F55',
      textStyle: { color: '#E8F0FE' },
      formatter: (p: any) => {
        const sol = paretoSolutions.value.find(s => s.id === p.name)
        return sol ? `<b>${sol.id}</b>${sol.isRecommended ? ' ⭐推荐' : ''}<br/>防洪：${sol.floodBenefit}<br/>发电：${sol.powerBenefit}<br/>供水：${sol.waterSupplyBenefit}<br/>生态：${sol.ecoBenefit}` : ''
      }
    },
    xAxis: { name: '防洪效益', nameTextStyle: { color: '#8BA3C7' }, axisLine: { lineStyle: { color: '#2A3F55' } }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } },
    yAxis: { name: '发电效益', nameTextStyle: { color: '#8BA3C7' }, axisLine: { lineStyle: { color: '#2A3F55' } }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } },
    series: [{
      type: 'scatter',
      data,
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,212,255,0.5)' } }
    }]
  })

  // 点击选中方案
  paretoChart.on('click', (params: any) => {
    const sol = paretoSolutions.value.find(s => s.id === params.name)
    if (sol) {
      selectedSolution.value = sol
      renderScheduleChart()
    }
  })
}

function renderScheduleChart() {
  if (!scheduleChartRef.value || !selectedSolution.value) return
  if (!scheduleChart) scheduleChart = echarts.init(scheduleChartRef.value)

  const sol = selectedSolution.value
  scheduleChart.setOption({
    backgroundColor: 'transparent',
    title: { text: `调度过程线 · ${sol.id}${sol.isRecommended ? ' ⭐推荐' : ''}`, textStyle: { color: '#E8F0FE', fontSize: 14 }, left: 8, top: 4 },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(13,27,42,0.9)', borderColor: '#2A3F55', textStyle: { color: '#E8F0FE' } },
    legend: { data: ['闸门开度 (%)', '泄流量 (m³/s)'], textStyle: { color: '#8BA3C7' }, right: 8, top: 4 },
    grid: { left: 60, right: 60, top: 48, bottom: 32 },
    xAxis: { type: 'category', data: sol.schedule.map(s => s.time), axisLine: { lineStyle: { color: '#2A3F55' } }, axisLabel: { color: '#8BA3C7' } },
    yAxis: [
      { type: 'value', name: '开度 (%)', nameTextStyle: { color: '#8BA3C7' }, axisLabel: { color: '#8BA3C7' }, splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } } },
      { type: 'value', name: '泄流量 (m³/s)', nameTextStyle: { color: '#8BA3C7' }, axisLabel: { color: '#8BA3C7' }, splitLine: { show: false } }
    ],
    series: [
      { name: '闸门开度 (%)', type: 'line', data: sol.schedule.map(s => s.gateOpening), smooth: true, lineStyle: { color: '#FA8C16', width: 2 }, itemStyle: { color: '#FA8C16' } },
      { name: '泄流量 (m³/s)', type: 'bar', yAxisIndex: 1, data: sol.schedule.map(s => s.discharge), barWidth: 16, itemStyle: { color: 'rgba(24,144,255,0.6)' } }
    ]
  })
}

function formatTime(ts: string): string {
  return new Date(ts).toLocaleString('zh-CN')
}

function alertTag(level: string) {
  const map: Record<string, { text: string; type: string }> = {
    RED: { text: '红色', type: 'danger' },
    ORANGE: { text: '橙色', type: 'warning' },
    YELLOW: { text: '黄色', type: 'warning' },
    BLUE: { text: '蓝色', type: 'primary' },
    NORMAL: { text: '正常', type: 'success' }
  }
  return map[level] || { text: level, type: 'info' }
}

function handleExport() {
  // [DEMO-ONLY] 导出功能占位
  alert('导出功能开发中，将在 Phase-2 实现 CSV/Excel 下载')
}

onMounted(() => loadData())
watch(selectedStation, () => loadData())
</script>

<template>
  <div class="detail-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button text @click="router.push('/dashboard')" style="color: var(--text-secondary);">← 返回大屏</el-button>
        <el-select v-model="selectedStation" placeholder="选择站点" style="width: 200px;" filterable>
          <el-option v-for="opt in stationOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-radio-group v-model="timeRange" size="small">
          <el-radio-button v-for="opt in timeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</el-radio-button>
        </el-radio-group>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" plain size="small" @click="handleExport">📥 导出数据</el-button>
      </div>
    </div>

    <!-- 内容区：上图下表 -->
    <div class="detail-body">
      <!-- 左侧：三联图 + 数据表 -->
      <div class="left-section">
        <div class="triple-chart card-panel">
          <div ref="tripleChartRef" style="width: 100%; height: 100%;"></div>
        </div>
        <div class="data-table card-panel">
          <div class="card-title">📋 数据明细</div>
          <el-table :data="pagedData" size="small" style="width: 100%;"
            :header-cell-style="{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderColor: 'var(--border-color)' }"
            :cell-style="{ background: 'transparent', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
          >
            <el-table-column prop="timestamp" label="时间" width="180" :formatter="(row: SensorReading) => formatTime(row.timestamp)" sortable />
            <el-table-column prop="waterLevel" label="水位 (m)" width="120" sortable />
            <el-table-column prop="rainfall" label="雨量 (mm/h)" width="120" sortable />
            <el-table-column prop="flow" label="流量 (m³/s)" width="120" sortable />
            <el-table-column prop="alertLevel" label="预警等级" width="100">
              <template #default="{ row }">
                <el-tag :type="alertTag(row.alertLevel).type as any" size="small">{{ alertTag(row.alertLevel).text }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="historyData.length"
            layout="total, prev, pager, next"
            small
            style="margin-top: 12px; justify-content: flex-end;"
          />
        </div>
      </div>

      <!-- 右侧：帕累托 + 调度过程线 -->
      <div class="right-section">
        <div class="pareto-chart card-panel">
          <div ref="paretoChartRef" style="width: 100%; height: 100%;"></div>
        </div>
        <div class="schedule-chart card-panel">
          <div ref="scheduleChartRef" style="width: 100%; height: 100%;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-page {
  width: 100%;
  height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-body {
  flex: 1;
  display: flex;
  gap: 12px;
  padding: 12px;
  overflow: hidden;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.triple-chart {
  height: 380px;
  flex-shrink: 0;
}

.data-table {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.right-section {
  width: 440px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pareto-chart, .schedule-chart {
  flex: 1;
}

/* Element Plus 暗色表格覆盖 */
:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
}

:deep(.el-radio-button__inner) {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-color: var(--border-color);
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

:deep(.el-select .el-input__wrapper) {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  box-shadow: none;
}

:deep(.el-select .el-input__inner) {
  color: var(--text-primary);
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-bg-color: var(--bg-tertiary);
}
</style>
