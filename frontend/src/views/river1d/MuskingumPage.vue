<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

type MuskingumCalibration = {
  dt_minutes: number
  train_ratio: number
  segments: number
  thresholds: number[]
  weights: { A: number; B: number }
  params: Array<{ k_hours: number; x: number }>
}

type MuskingumSeries = {
  time: string[]
  A?: number[]
  B?: number[]
  C_obs?: number[]
  C_sim?: number[]
  C_forecast?: number[]
}

type CalibrationResponse = {
  success: boolean
  algorithm: string
  sample_count: number
  train_count: number
  test_count: number
  calibration: MuskingumCalibration
  metrics: Record<string, number>
  series: MuskingumSeries
}

type ForecastResponse = {
  success: boolean
  model: string
  dt_minutes: number
  used_steps: number
  metrics: Record<string, number>
  series: MuskingumSeries
}

const router = useRouter()
const API_BASE = 'http://localhost:8084/api/hydrology/muskingum'

const form = ref({
  upstream_a: '2021_maskingun_three_stations_sheet2_A.csv',
  upstream_b: '2021_maskingun_three_stations_sheet3_B.csv',
  downstream_c: '2021_maskingun_three_stations_sheet1_C.csv',
  dt_minutes: 60,
  train_ratio: 0.7,
  segments: 3,
  iterations: 3500,
  forecast_steps: 72,
})

const calibrating = ref(false)
const forecasting = ref(false)
const calibrationResult = ref<CalibrationResponse | null>(null)
const forecastResult = ref<ForecastResponse | null>(null)
const errorText = ref('')

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const segmentRows = computed(() => {
  const c = calibrationResult.value?.calibration
  if (!c) return []
  return c.params.map((p, idx) => {
    const low = idx === 0 ? '-inf' : c.thresholds[idx - 1].toFixed(2)
    const high = idx === c.params.length - 1 ? '+inf' : c.thresholds[idx].toFixed(2)
    return {
      segment: idx + 1,
      inflowRange: `[${low}, ${high}]`,
      kHours: p.k_hours,
      x: p.x,
    }
  })
})

const calibrationMetricCards = computed(() => {
  const m = calibrationResult.value?.metrics
  if (!m) return []
  return [
    { label: '训练 RMSE', value: m.train_rmse ?? 0 },
    { label: '训练 NSE', value: m.train_nse ?? 0 },
    { label: '测试 RMSE', value: m.test_rmse ?? 0 },
    { label: '测试 NSE', value: m.test_nse ?? 0 },
    { label: '测试 MAPE(%)', value: m.test_mape ?? 0 },
  ]
})

const forecastMetricCards = computed(() => {
  const m = forecastResult.value?.metrics
  if (!m) return []
  return [
    { label: '预报 RMSE', value: m.forecast_rmse ?? 0 },
    { label: '预报 NSE', value: m.forecast_nse ?? 0 },
    { label: '预报 MAPE(%)', value: m.forecast_mape ?? 0 },
  ]
})

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  renderChart()
}

function renderChart() {
  if (!chart) return

  const baseSeries = calibrationResult.value?.series
  const useForecast = forecastResult.value?.series

  const source = useForecast ?? baseSeries
  if (!source || !source.time || source.time.length === 0) {
    chart.setOption({ title: { text: '暂无时序结果' } })
    return
  }

  const obs = source.C_obs ?? []
  const sim = source.C_forecast ?? source.C_sim ?? []
  const time = source.time.map((t) => t.replace('T', ' ').slice(0, 16))

  chart.setOption({
    backgroundColor: '#0f1a29',
    animation: true,
    tooltip: { trigger: 'axis' },
    legend: {
      top: 10,
      textStyle: { color: '#dbeafe' },
      data: ['下游观测 C', useForecast ? '下游预报 C' : '下游模拟 C'],
    },
    grid: { left: 60, right: 30, top: 45, bottom: 40 },
    xAxis: {
      type: 'category',
      data: time,
      axisLabel: { color: '#9fb3c8', interval: Math.ceil(time.length / 8) },
      axisLine: { lineStyle: { color: '#2d3f55' } },
    },
    yAxis: {
      type: 'value',
      name: '流量',
      nameTextStyle: { color: '#9fb3c8' },
      axisLabel: { color: '#9fb3c8' },
      splitLine: { lineStyle: { color: '#243447' } },
    },
    series: [
      {
        name: '下游观测 C',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#f59e0b' },
        data: obs,
      },
      {
        name: useForecast ? '下游预报 C' : '下游模拟 C',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#22c55e' },
        data: sim,
      },
    ],
  })
}

async function calibrateParams() {
  errorText.value = ''
  forecastResult.value = null
  calibrating.value = true
  try {
    const resp = await fetch(`${API_BASE}/calibrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset: {
          upstream_a: form.value.upstream_a,
          upstream_b: form.value.upstream_b,
          downstream_c: form.value.downstream_c,
        },
        dt_minutes: form.value.dt_minutes,
        train_ratio: form.value.train_ratio,
        segments: form.value.segments,
        iterations: form.value.iterations,
      }),
    })

    if (!resp.ok) {
      throw new Error(`率定失败: HTTP ${resp.status}`)
    }

    const data = (await resp.json()) as CalibrationResponse
    calibrationResult.value = data
    ElMessage.success('分段马斯金根参数率定完成')
    await nextTick()
    renderChart()
  } catch (err) {
    errorText.value = err instanceof Error ? err.message : '率定失败'
    ElMessage.error(errorText.value)
  } finally {
    calibrating.value = false
  }
}

async function runForecast() {
  if (!calibrationResult.value?.calibration) {
    ElMessage.warning('请先完成参数率定')
    return
  }

  errorText.value = ''
  forecasting.value = true
  try {
    const resp = await fetch(`${API_BASE}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset: {
          upstream_a: form.value.upstream_a,
          upstream_b: form.value.upstream_b,
          downstream_c: form.value.downstream_c,
        },
        forecast_steps: form.value.forecast_steps,
        use_last_calibration: true,
        calibration: calibrationResult.value.calibration,
      }),
    })

    if (!resp.ok) {
      throw new Error(`预报失败: HTTP ${resp.status}`)
    }

    forecastResult.value = (await resp.json()) as ForecastResponse
    ElMessage.success('流量预报完成')
    await nextTick()
    renderChart()
  } catch (err) {
    errorText.value = err instanceof Error ? err.message : '预报失败'
    ElMessage.error(errorText.value)
  } finally {
    forecasting.value = false
  }
}

function goBack() {
  router.push('/river1d')
}

watch(
  () => [calibrationResult.value, forecastResult.value],
  () => {
    renderChart()
  }
)

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})

function handleResize() {
  chart?.resize()
}
</script>

<template>
  <div class="muskingum-page">
    <header class="head">
      <div class="left">
        <el-button plain @click="goBack">返回 River1D</el-button>
        <h2>分段马斯金根法 · 参数率定与流量预报</h2>
      </div>
      <div class="right">
        <el-button type="primary" :loading="calibrating" @click="calibrateParams">执行参数率定</el-button>
        <el-button type="success" :loading="forecasting" @click="runForecast">执行流量预报</el-button>
      </div>
    </header>

    <section class="panel form-grid">
      <div class="fg">
        <label>上游 A 文件</label>
        <input v-model="form.upstream_a" class="input" />
      </div>
      <div class="fg">
        <label>上游 B 文件</label>
        <input v-model="form.upstream_b" class="input" />
      </div>
      <div class="fg">
        <label>下游 C 文件</label>
        <input v-model="form.downstream_c" class="input" />
      </div>
      <div class="fg">
        <label>时间步长 (min)</label>
        <input v-model.number="form.dt_minutes" type="number" min="10" class="input" />
      </div>
      <div class="fg">
        <label>训练占比</label>
        <input v-model.number="form.train_ratio" type="number" min="0.55" max="0.9" step="0.01" class="input" />
      </div>
      <div class="fg">
        <label>分段数</label>
        <input v-model.number="form.segments" type="number" min="2" max="6" class="input" />
      </div>
      <div class="fg">
        <label>优化迭代数</label>
        <input v-model.number="form.iterations" type="number" min="200" step="100" class="input" />
      </div>
      <div class="fg">
        <label>预报步数</label>
        <input v-model.number="form.forecast_steps" type="number" min="12" class="input" />
      </div>
    </section>

    <section v-if="errorText" class="panel error-box">{{ errorText }}</section>

    <section class="cards-wrap" v-if="calibrationMetricCards.length">
      <div class="metric-card" v-for="item in calibrationMetricCards" :key="item.label">
        <div class="label">{{ item.label }}</div>
        <div class="value">{{ Number(item.value).toFixed(4) }}</div>
      </div>
    </section>

    <section class="cards-wrap" v-if="forecastMetricCards.length">
      <div class="metric-card metric-forecast" v-for="item in forecastMetricCards" :key="item.label">
        <div class="label">{{ item.label }}</div>
        <div class="value">{{ Number(item.value).toFixed(4) }}</div>
      </div>
    </section>

    <section class="panel" v-if="calibrationResult?.calibration">
      <h3>率定结果</h3>
      <div class="weights">
        <span>上游权重 A: {{ calibrationResult.calibration.weights.A.toFixed(4) }}</span>
        <span>上游权重 B: {{ calibrationResult.calibration.weights.B.toFixed(4) }}</span>
      </div>
      <table class="param-table">
        <thead>
          <tr>
            <th>分段</th>
            <th>流量区间</th>
            <th>K (h)</th>
            <th>x</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in segmentRows" :key="row.segment">
            <td>{{ row.segment }}</td>
            <td>{{ row.inflowRange }}</td>
            <td>{{ row.kHours.toFixed(4) }}</td>
            <td>{{ row.x.toFixed(4) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="panel chart-panel">
      <h3>下游 C 过程线对比</h3>
      <div ref="chartRef" class="chart"></div>
    </section>
  </div>
</template>

<style scoped>
.muskingum-page {
  min-height: 100vh;
  padding: 14px;
  background: linear-gradient(160deg, #0d1b2a 0%, #10253a 40%, #17314b 100%);
  color: #e8f0fe;
  overflow: auto;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.left h2 {
  font-size: 18px;
  letter-spacing: 0.2px;
}

.right {
  display: flex;
  gap: 10px;
}

.panel {
  border: 1px solid #2a3f55;
  border-radius: 10px;
  background: rgba(18, 39, 60, 0.92);
  padding: 12px;
  margin-bottom: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 10px;
}

.fg {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.fg label {
  font-size: 12px;
  color: #9fb3c8;
}

.input {
  height: 34px;
  border: 1px solid #2e4762;
  border-radius: 6px;
  background: #0f2437;
  color: #e8f0fe;
  padding: 0 10px;
}

.error-box {
  border-color: #7f1d1d;
  background: rgba(127, 29, 29, 0.2);
  color: #fecaca;
}

.cards-wrap {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.metric-card {
  border: 1px solid #2b4868;
  border-radius: 8px;
  background: rgba(16, 37, 58, 0.92);
  padding: 10px;
}

.metric-forecast {
  border-color: #1f6f4a;
  background: rgba(11, 52, 35, 0.9);
}

.metric-card .label {
  font-size: 12px;
  color: #9fb3c8;
}

.metric-card .value {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 700;
  color: #e8f0fe;
}

.weights {
  display: flex;
  gap: 20px;
  margin: 8px 0 12px;
  color: #b6d4f2;
  font-size: 13px;
}

.param-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.param-table th,
.param-table td {
  border: 1px solid #2a3f55;
  padding: 8px;
  text-align: center;
}

.param-table th {
  background: #10253a;
  color: #aac4df;
}

.chart-panel h3 {
  margin-bottom: 8px;
}

.chart {
  width: 100%;
  height: 360px;
}

@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(180px, 1fr));
  }

  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .right {
    width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 700px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .left h2 {
    font-size: 16px;
  }
}
</style>
