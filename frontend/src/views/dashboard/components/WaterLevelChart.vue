<script setup lang="ts">
/**
 * 水位趋势 ECharts 折线图
 * [DEMO-ONLY] 使用 Mock 历史数据，每 3 秒追加新数据点模拟实时效果
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { generateHistory24h, generateMockReading } from '@/mock/station'

const props = defineProps<{
  stationId: string
}>()

const chartContainer = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let timer: ReturnType<typeof setInterval> | null = null

function initChart() {
  if (!chartContainer.value) return
  chart = echarts.init(chartContainer.value)

  const history = generateHistory24h(props.stationId)
  const times = history.map(d => {
    const date = new Date(d.timestamp)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  })
  const waterLevels = history.map(d => d.waterLevel)
  const rainfalls = history.map(d => d.rainfall)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: '📈 水位趋势 (24h)',
      textStyle: { color: '#E8F0FE', fontSize: 14, fontWeight: 500 },
      left: 8,
      top: 4
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 27, 42, 0.9)',
      borderColor: '#2A3F55',
      textStyle: { color: '#E8F0FE', fontSize: 12 }
    },
    legend: {
      data: ['水位 (m)', '雨量 (mm/h)'],
      textStyle: { color: '#8BA3C7', fontSize: 11 },
      right: 8,
      top: 4
    },
    grid: { left: 50, right: 50, top: 48, bottom: 32 },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#2A3F55' } },
      axisLabel: { color: '#8BA3C7', fontSize: 10 },
      splitLine: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: { color: '#8BA3C7', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2A3F55' } },
        axisLabel: { color: '#8BA3C7', fontSize: 10 },
        splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } }
      },
      {
        type: 'value',
        name: '雨量 (mm/h)',
        nameTextStyle: { color: '#8BA3C7', fontSize: 10 },
        axisLine: { lineStyle: { color: '#2A3F55' } },
        axisLabel: { color: '#8BA3C7', fontSize: 10 },
        splitLine: { show: false },
        inverse: true
      }
    ],
    series: [
      {
        name: '水位 (m)',
        type: 'line',
        data: waterLevels,
        smooth: true,
        lineStyle: { color: '#00D4FF', width: 2 },
        itemStyle: { color: '#00D4FF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.02)' }
          ])
        },
        // 警戒线
        markLine: {
          silent: true,
          lineStyle: { color: '#F5222D', type: 'dashed', width: 1 },
          data: [{ yAxis: 28, name: '保证水位', label: { color: '#F5222D', fontSize: 10 } }]
        }
      },
      {
        name: '雨量 (mm/h)',
        type: 'bar',
        yAxisIndex: 1,
        data: rainfalls,
        barWidth: 6,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#1890FF' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.2)' }
          ])
        }
      }
    ]
  }

  chart.setOption(option)

  // [DEMO-ONLY] 动态追加数据模拟实时效果
  timer = setInterval(() => {
    const reading = generateMockReading(props.stationId)
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

    times.push(timeStr)
    waterLevels.push(reading.waterLevel)
    rainfalls.push(reading.rainfall)

    // 保持 25 个点
    if (times.length > 25) {
      times.shift()
      waterLevels.shift()
      rainfalls.shift()
    }

    chart?.setOption({
      xAxis: { data: times },
      series: [
        { data: waterLevels },
        { data: rainfalls }
      ]
    })
  }, 3000)
}

onMounted(() => initChart())

onUnmounted(() => {
  if (timer) clearInterval(timer)
  chart?.dispose()
})

// 切换站点时重绘
watch(() => props.stationId, () => {
  if (timer) clearInterval(timer)
  chart?.dispose()
  initChart()
})
</script>

<template>
  <div class="water-chart card-panel">
    <div ref="chartContainer" style="width: 100%; height: 100%;"></div>
  </div>
</template>

<style scoped>
.water-chart {
  height: 100%;
  padding: 4px;
  overflow: hidden;
}
</style>
