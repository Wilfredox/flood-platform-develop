<script setup lang="ts">
/**
 * R1DRightPanel.vue — River1D 右侧面板
 * R4: 图层管理与统计卡片 (图层开关、清空、数量统计)
 * R5: 拓扑处理 (容差设置, 节点生成, 报告展示)
 */
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useRiver1dStore } from '@/stores/useRiver1dStore'
import type { River, Bank, CrossSection, Structure } from '@/types/river1d'

const store = useRiver1dStore()
const attrForm = ref<Record<string, any>>({})

// ── 图层子列表展开状态 ────────────────────────────────
const layerExpanded = ref<Record<string, boolean>>({
  river: false,
  bank: false,
  section: false,
  structure: false,
  nodes: false,
})
function toggleLayerExpand(key: string) {
  layerExpanded.value[key] = !layerExpanded.value[key]
}

// ── 操作日志 ──────────────────────────────────────────
interface LogEntry {
  id: number
  time: string
  level: 'info' | 'success' | 'warn' | 'error'
  msg: string
}
let _logSeq = 0
const opLogs = ref<LogEntry[]>([])
const logExpanded = ref(true)

function addLog(msg: string, level: LogEntry['level'] = 'info') {
  const now = new Date()
  const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`
  opLogs.value.unshift({ id: ++_logSeq, time, level, msg })
  if (opLogs.value.length > 200) opLogs.value.length = 200
}

// 监听图层变化自动记录日志
let prevRiverLen = 0, prevBankLen = 0, prevSecLen = 0, prevStrLen = 0, prevNodeLen = 0
watch(
  () => [store.rivers.length, store.banks.length, store.sections.length, store.structures.length, store.nodes.length],
  ([rL, bL, sL, stL, nL]) => {
    if (rL > prevRiverLen) addLog(`新增河道中心线，当前共 ${rL} 条河道`, 'success')
    else if (rL < prevRiverLen) addLog(`清空/删除河道，当前共 ${rL} 条河道`, 'warn')
    if (bL > prevBankLen) addLog(`新增岸线（堤防），当前共 ${bL} 条`, 'success')
    else if (bL < prevBankLen) addLog(`清空/删除岸线，当前共 ${bL} 条`, 'warn')
    if (sL > prevSecLen) addLog(`新增横断面，当前共 ${sL} 个`, 'success')
    else if (sL < prevSecLen) addLog(`清空/删除断面，当前共 ${sL} 个`, 'warn')
    if (stL > prevStrLen) addLog(`新增水工建筑物，当前共 ${stL} 个`, 'success')
    else if (stL < prevStrLen) addLog(`清空/删除建筑物，当前共 ${stL} 个`, 'warn')
    if (nL > prevNodeLen) addLog(`生成拓扑节点 ${nL} 个`, 'success')
    else if (nL < prevNodeLen && nL === 0) addLog('清空拓扑节点', 'warn')
    prevRiverLen = rL; prevBankLen = bL; prevSecLen = sL; prevStrLen = stL; prevNodeLen = nL
  }
)
watch(
  () => store.activeTool,
  (tool) => {
    const nameMap: Record<string, string> = {
      select: '选择', river: '河道中心线绘制', bank: '岸线绘制',
      section: '横断面绘制', structure: '水工建筑物绘制', node: '节点编辑'
    }
    addLog(`切换工具：${nameMap[tool] ?? tool}`)
  }
)
watch(
  () => store.topoReport,
  (r) => {
    if (!r) return
    if (r.ok) addLog('拓扑检查通过，未发现错误', 'success')
    else addLog(`拓扑检查完成，发现 ${r.issues.length} 个错误、${r.warnings.length} 个警告`, r.issues.length > 0 ? 'error' : 'warn')
  }
)

// 监听工具绘制开始（通过 store.isDirty 变化粗略感知）
watch(() => store.isDirty, (v) => {
  if (v) addLog('项目已修改（未保存）', 'info')
})
const API_BASE = 'http://localhost:8084/api/river1d/projects'

// Tabs: build (建模), props (属性), params (参数), compute (计算)
const activeTab = ref('build')

function switchTab(tab: 'build' | 'props' | 'params' | 'compute') {
  activeTab.value = tab
  if (tab === 'props') {
    // 进入属性页时默认启用选择工具，避免仍停留在绘制模式导致无法选中要素。
    store.setTool('select')
  }
}

function enableSelectFromProps() {
  // 显式启用选择模式，并保持停留在属性页等待用户点击地图要素。
  store.setTool('select')
  activeTab.value = 'props'
}

watch(
  () => store.selectedFeature,
  (feature) => {
    // 一旦选中要素，自动聚焦到属性页，避免“已选中但看不到属性”的错觉。
    if (feature && activeTab.value !== 'props') {
      activeTab.value = 'props'
    }
  }
)

watch(
  () => store.activeTool,
  (tool) => {
    // 在属性页切到绘制工具时，自动返回建模页，避免属性页与绘制状态冲突。
    if (activeTab.value === 'props' && tool !== 'select') {
      activeTab.value = 'build'
    }
  }
)

const computeParams = ref({
  mainChannelN: 0.03,
  dtSeconds: 60,
  totalHours: 24
})
const computeTaskId = ref('')
const computeStatus = ref<'IDLE' | 'RUNNING' | 'SUCCEEDED' | 'FAILED'>('IDLE')
const computeProgress = ref(0)
const computeStage = ref('待启动')
const computeLogs = ref<string[]>([])
let computePollTimer: ReturnType<typeof setInterval> | null = null

// 展开/收起面板区块 (Accordion)
const sectionOpen = ref<Record<string, boolean>>({
  layers: true,
  topo: true,
  proj: true,
  roughness: true,
  bc: true,
  densify: true,
  simParams: true,
  runCtrl: true,
  log: true
})
function toggleSection(key: string) {
  sectionOpen.value[key] = !sectionOpen.value[key]
}

const emit = defineEmits<{
  (e: 'genNodes', showReport: boolean): void
  (e: 'checkTopo'): void
  (e: 'flyTo', coords: Array<{ lat: number; lng: number }>): void
}>()

function doCheckTopo() {
  addLog('执行拓扑检查…')
  store.checkTopo()
  emit('checkTopo')
}

function doGenNodes() {
  addLog('执行自动生成节点…')
  emit('genNodes', false)
}

// flyTo 跳转辅助
function flyToFeature(f: River | Bank | CrossSection | Structure) {
  let coords: Array<{ lat: number; lng: number }> = []
  if (f.type === 'river') {
    f.reaches.forEach(rc => coords.push(...rc.coords))
  } else {
    coords = f.coords
  }
  if (coords.length) {
    const name = (f as any).attrs?.name || f.id
    addLog(`定位至：${name}`)
    emit('flyTo', coords)
    // 同时选中要素
    store.selectFeature(f)
  }
}

type EditableField = {
  key: string
  label: string
  type?: 'text' | 'number'
  options?: string[]
  multiline?: boolean
}

const editableFields = computed(() => {
  const f = store.selectedFeature
  if (!f) return [] as EditableField[]
  if (f.type === 'river') {
    return [
      { key: 'name', label: '河道名称' },
      { key: 'reachName', label: '河段名称' },
      { key: 'fromName', label: '起点名称' },
      { key: 'toName', label: '终点名称' },
      { key: 'notes', label: '备注', multiline: true }
    ]
  }
  if (f.type === 'bank') {
    return [
      { key: 'name', label: '岸线名称' },
      { key: 'side', label: '侧别', options: ['左岸', '右岸', '无侧别'] },
      { key: 'notes', label: '备注', multiline: true }
    ]
  }
  if (f.type === 'section') {
    return [
      { key: 'name', label: '断面名称' },
      { key: 'station', label: '断面里程', type: 'number' },
      { key: 'reachId', label: '所属河段' },
      { key: 'notes', label: '备注', multiline: true }
    ]
  }
  return [
    { key: 'name', label: '建筑物名称' },
    { key: 'stype', label: '类型', options: ['水闸', '堰/溢流堰', '泵站', '桥梁', '涵洞', '其他'] },
    { key: 'station', label: '位置里程', type: 'number' },
    { key: 'elev', label: '高程', type: 'number' },
    { key: 'width', label: '宽度', type: 'number' },
    { key: 'notes', label: '备注', multiline: true }
  ]
})

const sectionProfileRows = computed(() => {
  if (store.selectedFeature?.type !== 'section') return [] as Array<{ dist: number; elev: number }>
  if (!Array.isArray(attrForm.value.profile)) {
    attrForm.value.profile = []
  }
  return attrForm.value.profile as Array<{ dist: number; elev: number }>
})

const sectionProfileSvgPath = computed(() => {
  const rows = [...sectionProfileRows.value].sort((a, b) => a.dist - b.dist)
  if (rows.length < 2) return ''

  const width = 280
  const height = 120
  const pad = 10
  const dists = rows.map(r => r.dist)
  const elevs = rows.map(r => r.elev)
  const minX = Math.min(...dists)
  const maxX = Math.max(...dists)
  const minY = Math.min(...elevs)
  const maxY = Math.max(...elevs)
  const spanX = Math.max(1e-6, maxX - minX)
  const spanY = Math.max(1e-6, maxY - minY)

  return rows.map((r, idx) => {
    const x = pad + ((r.dist - minX) / spanX) * (width - pad * 2)
    const y = height - pad - ((r.elev - minY) / spanY) * (height - pad * 2)
    return `${idx === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
  }).join(' ')
})

watch(
  () => store.selectedFeature,
  (feature) => {
    if (!feature) {
      attrForm.value = {}
      return
    }

    const nextForm = { ...feature.attrs } as Record<string, unknown>
    editableFields.value.forEach(fd => {
      if (fd.options && (nextForm[fd.key] === undefined || nextForm[fd.key] === null || nextForm[fd.key] === '')) {
        nextForm[fd.key] = fd.options[0]
      }
      if (fd.type === 'number' && (nextForm[fd.key] === undefined || nextForm[fd.key] === null || nextForm[fd.key] === '')) {
        nextForm[fd.key] = 0
      }
      if (fd.multiline && nextForm[fd.key] === undefined) {
        nextForm[fd.key] = ''
      }
    })
    attrForm.value = nextForm
  },
  { immediate: true }
)

function saveAttrs() {
  const payload = { ...attrForm.value }
  editableFields.value.forEach(fd => {
    if (fd.type === 'number' && payload[fd.key] !== undefined && payload[fd.key] !== '') {
      payload[fd.key] = Number(payload[fd.key])
    }
    if (fd.options && payload[fd.key] !== undefined) {
      payload[fd.key] = String(payload[fd.key])
    }
    if (fd.multiline && payload[fd.key] !== undefined) {
      payload[fd.key] = String(payload[fd.key])
    }
  })
  store.updateSelectedAttrs(payload)
  const name = payload.name || store.selectedFeature?.id || '未命名'
  addLog(`保存属性：${name}`, 'success')
}

function addSectionProfileRow() {
  if (store.selectedFeature?.type !== 'section') return
  const rows = [...sectionProfileRows.value]
  const last = rows[rows.length - 1]
  sectionProfileRows.value.push({
    dist: last ? Number(last.dist) + 10 : 0,
    elev: last ? Number(last.elev) : 0
  })
}

function removeSectionProfileRow(index: number) {
  if (store.selectedFeature?.type !== 'section') return
  sectionProfileRows.value.splice(index, 1)
}

function normalizeSectionProfile() {
  if (store.selectedFeature?.type !== 'section') return
  const rows = [...sectionProfileRows.value]
    .filter(r => Number.isFinite(r.dist) && Number.isFinite(r.elev))
    .sort((a, b) => a.dist - b.dist)
  attrForm.value.profile = rows
}

function stopComputePolling() {
  if (computePollTimer) {
    clearInterval(computePollTimer)
    computePollTimer = null
  }
}

function buildDraftPayload() {
  return {
    projectName: store.project.name,
    crs: store.project.crs,
    description: store.project.desc,
    rivers: store.rivers.flatMap(river =>
      river.reaches.map(reach => ({
        id: reach.id,
        name: reach.name || river.attrs.name,
        coords: reach.coords.map(pt => ({ lat: pt.lat, lng: pt.lng }))
      }))
    ),
    banks: store.banks.map(bank => ({
      id: bank.id,
      name: String(bank.attrs.name || ''),
      coords: bank.coords.map(pt => ({ lat: pt.lat, lng: pt.lng }))
    })),
    sections: store.sections.map(section => ({
      id: section.id,
      name: String(section.attrs.name || ''),
      station: Number(section.attrs.station || 0),
      coords: section.coords.map(pt => ({ lat: pt.lat, lng: pt.lng })),
      profile: Array.isArray(section.attrs.profile)
        ? section.attrs.profile
            .map(p => ({
              dist: Number((p as { dist?: unknown }).dist ?? 0),
              elev: Number((p as { elev?: unknown }).elev ?? 0)
            }))
            .filter(p => Number.isFinite(p.dist) && Number.isFinite(p.elev))
        : []
    })),
    structures: store.structures.map(st => ({
      id: st.id,
      name: String(st.attrs.name || ''),
      coords: st.coords.map(pt => ({ lat: pt.lat, lng: pt.lng }))
    })),
    nodes: store.nodes.map(node => ({
      id: node.id,
      lat: node.lat,
      lng: node.lng,
      nodeType: node.nodeType
    }))
  }
}

async function pollComputeStatus() {
  if (!computeTaskId.value) return
  try {
    const resp = await fetch(`${API_BASE}/compute/${computeTaskId.value}/status`)
    if (!resp.ok) {
      throw new Error(`状态查询失败: HTTP ${resp.status}`)
    }
    const data = await resp.json()
    computeProgress.value = Number(data.progress ?? 0)
    computeStage.value = String(data.stage ?? '处理中')
    computeStatus.value = String(data.status ?? 'RUNNING') as 'IDLE' | 'RUNNING' | 'SUCCEEDED' | 'FAILED'
    computeLogs.value = Array.isArray(data.logs) ? data.logs.map((x: unknown) => String(x)) : []
    if (computeStatus.value === 'SUCCEEDED') {
      stopComputePolling()
    }
  } catch (err) {
    computeStatus.value = 'FAILED'
    computeLogs.value.push(`[ERROR] ${err instanceof Error ? err.message : '状态查询异常'}`)
    stopComputePolling()
  }
}

async function startCompute() {
  if (computeStatus.value === 'RUNNING') {
    return
  }

  stopComputePolling()
  computeStatus.value = 'RUNNING'
  computeProgress.value = 0
  computeStage.value = '提交任务中'
  computeLogs.value = ['[INFO] 正在提交 River1D 计算任务...']

  try {
    const runResp = await fetch(`${API_BASE}/compute/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project: buildDraftPayload(),
        params: {
          mainChannelN: computeParams.value.mainChannelN,
          dtSeconds: computeParams.value.dtSeconds,
          totalHours: computeParams.value.totalHours
        }
      })
    })
    if (!runResp.ok) {
      throw new Error(`任务启动失败: HTTP ${runResp.status}`)
    }

    const runData = await runResp.json()
    computeTaskId.value = String(runData.taskId || '')
    computeLogs.value.push(`[INFO] 任务已启动，taskId=${computeTaskId.value}`)

    await pollComputeStatus()
    if (computeStatus.value === 'RUNNING') {
      computePollTimer = setInterval(() => {
        void pollComputeStatus()
      }, 2000)
    }
  } catch (err) {
    computeStatus.value = 'FAILED'
    computeStage.value = '提交失败'
    computeLogs.value.push(`[ERROR] ${err instanceof Error ? err.message : '任务启动异常'}`)
    stopComputePolling()
  }
}

onBeforeUnmount(() => {
  stopComputePolling()
})
</script>

<template>
  <div class="rpanel">
    <!-- Tabs -->
    <div class="rp-tabs">
      <div class="rp-tab" :class="{ active: activeTab === 'build' }" @click="switchTab('build')">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 12L5 8 7.5 9.5 12 4"/><path d="M2 2V13H13"/>
        </svg>
        建模
      </div>
      <div class="rp-tab" :class="{ active: activeTab === 'props' }" @click="switchTab('props')">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="2" width="10" height="10" rx="1.5"/><path d="M5 6H9M5 8.5H7.5"/>
        </svg>
        属性
      </div>
      <div class="rp-tab" :class="{ active: activeTab === 'params' }" @click="switchTab('params')">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="7" cy="4" r="1.5"/><circle cx="3.5" cy="10" r="1.5"/><circle cx="10.5" cy="10" r="1.5"/><path d="M2 4H5.5M8.5 4H12M5 10H8"/>
        </svg>
        参数
      </div>
      <div class="rp-tab" :class="{ active: activeTab === 'compute' }" @click="switchTab('compute')">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
          <path d="M3 2L10 7 3 12Z"/>
        </svg>
        计算
      </div>
    </div>

    <!-- Body: 建模 R4 + R5 -->
    <div v-show="activeTab === 'build'" class="rp-body">
      <!-- 统计卡片 R4 -->
      <div class="stats-row">
        <div class="sc"><div class="sc-val">{{ store.stats.riverCount }}</div><div class="sc-lbl">河道</div></div>
        <div class="sc"><div class="sc-val">{{ store.stats.reachCount }}</div><div class="sc-lbl">河段</div></div>
        <div class="sc"><div class="sc-val">{{ store.stats.sectionCount }}</div><div class="sc-lbl">断面</div></div>
        <div class="sc"><div class="sc-val">{{ store.stats.nodeCount }}</div><div class="sc-lbl">节点</div></div>
      </div>

      <!-- 图层管理 R4 -->
      <div class="ps">
        <div class="psh" :class="{ open: sectionOpen.layers }" @click="toggleSection('layers')">
          <div class="psh-l">
            <div class="psh-ico" style="background:#e8f0ff;color:#1a6cff">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="1" y="1" width="9" height="2.5" rx=".5"/><rect x="1" y="5" width="9" height="2.5" rx=".5"/>
              </svg>
            </div>
            图层管理
          </div>
          <span class="psh-arr">▾</span>
        </div>
        <div v-show="sectionOpen.layers" class="psb open">
          <ul class="layer-list">
            <!-- 河道 -->
            <li class="li">
              <input type="checkbox" class="li-cb" v-model="store.layerVisible.river">
              <div class="li-sw" :style="{ background: store.layerStyles.river.color }"></div>
              <div class="li-info" @click="toggleLayerExpand('river')" style="cursor:pointer">
                <div class="li-name">河道中心线 <span class="li-expand-arrow">{{ layerExpanded.river ? '▴' : '▾' }}</span></div>
                <div class="li-meta">{{ store.stats.riverCount }} 条河道 · {{ store.stats.reachCount }} 个河段</div>
              </div>
              <div class="la">
                <button class="la-btn" title="绘制" @click="store.setTool('river')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9L7 4M8 3L9 5L7 4"/></svg>
                </button>
                <button class="la-btn del" title="清空" @click="store.clearLayer('river')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3L8 8M8 3L3 8"/></svg>
                </button>
              </div>
            </li>
            <!-- 河道子列表 -->
            <li v-if="layerExpanded.river && store.rivers.length > 0" class="li-sublist">
              <ul>
                <li
                  v-for="r in store.rivers"
                  :key="r.id"
                  class="li-sub-item"
                  @click="flyToFeature(r)"
                >
                  <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 7L4 2L7 7"/></svg>
                  <span class="li-sub-name">{{ r.attrs.name || r.id }}</span>
                  <span class="li-sub-meta">{{ r.reaches.length }} 段</span>
                </li>
              </ul>
            </li>
            <li v-if="layerExpanded.river && store.rivers.length === 0" class="li-sub-empty">暂无河道</li>

            <!-- 岸线 -->
            <li class="li">
              <input type="checkbox" class="li-cb" v-model="store.layerVisible.bank">
              <div class="li-sw" :style="{ background: store.layerStyles.bank.color }"></div>
              <div class="li-info" @click="toggleLayerExpand('bank')" style="cursor:pointer">
                <div class="li-name">岸线（堤防）<span class="li-expand-arrow">{{ layerExpanded.bank ? '▴' : '▾' }}</span></div>
                <div class="li-meta">{{ store.stats.bankCount }} 条 · 多节点折线</div>
              </div>
              <div class="la">
                <button class="la-btn" title="绘制" @click="store.setTool('bank')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9L7 4M8 3L9 5L7 4"/></svg>
                </button>
                <button class="la-btn del" title="清空" @click="store.clearLayer('bank')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3L8 8M8 3L3 8"/></svg>
                </button>
              </div>
            </li>
            <li v-if="layerExpanded.bank && store.banks.length > 0" class="li-sublist">
              <ul>
                <li
                  v-for="b in store.banks"
                  :key="b.id"
                  class="li-sub-item"
                  @click="flyToFeature(b)"
                >
                  <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 4H7M1 2H7M1 6H5"/></svg>
                  <span class="li-sub-name">{{ b.attrs.name || b.id }}</span>
                  <span class="li-sub-meta">{{ b.attrs.side || '' }}</span>
                </li>
              </ul>
            </li>
            <li v-if="layerExpanded.bank && store.banks.length === 0" class="li-sub-empty">暂无岸线</li>

            <!-- 断面 -->
            <li class="li">
              <input type="checkbox" class="li-cb" v-model="store.layerVisible.section">
              <div class="li-sw" :style="{ background: store.layerStyles.section.color }"></div>
              <div class="li-info" @click="toggleLayerExpand('section')" style="cursor:pointer">
                <div class="li-name">横断面 <span class="li-expand-arrow">{{ layerExpanded.section ? '▴' : '▾' }}</span></div>
                <div class="li-meta">{{ store.stats.sectionCount }} 个 · 单线段</div>
              </div>
              <div class="la">
                <button class="la-btn" title="绘制" @click="store.setTool('section')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9L7 4M8 3L9 5L7 4"/></svg>
                </button>
                <button class="la-btn del" title="清空" @click="store.clearLayer('section')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3L8 8M8 3L3 8"/></svg>
                </button>
              </div>
            </li>
            <li v-if="layerExpanded.section && store.sections.length > 0" class="li-sublist">
              <ul>
                <li
                  v-for="s in store.sections"
                  :key="s.id"
                  class="li-sub-item"
                  @click="flyToFeature(s)"
                >
                  <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 4H7"/></svg>
                  <span class="li-sub-name">{{ s.attrs.name || s.id }}</span>
                  <span class="li-sub-meta">{{ s.attrs.station ? `${s.attrs.station}m` : '' }}</span>
                </li>
              </ul>
            </li>
            <li v-if="layerExpanded.section && store.sections.length === 0" class="li-sub-empty">暂无断面</li>

            <!-- 建筑物 -->
            <li class="li">
              <input type="checkbox" class="li-cb" v-model="store.layerVisible.structure">
              <div class="li-sw" :style="{ background: store.layerStyles.structure.color }"></div>
              <div class="li-info" @click="toggleLayerExpand('structure')" style="cursor:pointer">
                <div class="li-name">水工建筑物 <span class="li-expand-arrow">{{ layerExpanded.structure ? '▴' : '▾' }}</span></div>
                <div class="li-meta">{{ store.stats.structureCount }} 个 · 单线段</div>
              </div>
              <div class="la">
                <button class="la-btn" title="绘制" @click="store.setTool('structure')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9L7 4M8 3L9 5L7 4"/></svg>
                </button>
                <button class="la-btn del" title="清空" @click="store.clearLayer('structure')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3L8 8M8 3L3 8"/></svg>
                </button>
              </div>
            </li>
            <li v-if="layerExpanded.structure && store.structures.length > 0" class="li-sublist">
              <ul>
                <li
                  v-for="s in store.structures"
                  :key="s.id"
                  class="li-sub-item"
                  @click="flyToFeature(s)"
                >
                  <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="2" width="6" height="4" rx="0.5"/></svg>
                  <span class="li-sub-name">{{ s.attrs.name || s.id }}</span>
                  <span class="li-sub-meta">{{ s.attrs.stype || '' }}</span>
                </li>
              </ul>
            </li>
            <li v-if="layerExpanded.structure && store.structures.length === 0" class="li-sub-empty">暂无建筑物</li>

            <!-- 节点 -->
            <li class="li">
              <input type="checkbox" class="li-cb" v-model="store.layerVisible.nodes">
              <div class="li-sw" :style="{ background: store.nodeStyle.colorJunction }"></div>
              <div class="li-info">
                <div class="li-name">拓扑节点</div>
                <div class="li-meta">{{ store.stats.nodeCount }} 个 · 河道首末端点</div>
              </div>
              <div class="la">
                <button class="la-btn del" title="清空" @click="store.clearLayer('nodes')">
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3L8 8M8 3L3 8"/></svg>
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 拓扑处理 R5 -->
      <div class="ps">
        <div class="psh" :class="{ open: sectionOpen.topo }" @click="toggleSection('topo')">
          <div class="psh-l">
            <div class="psh-ico" style="background:#e0f7f1;color:#0a9396">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="5.5" cy="3" r="1.5"/><circle cx="2" cy="8.5" r="1.5"/><circle cx="9" cy="8.5" r="1.5"/><path d="M4.7 4.5L2.5 7M6.3 4.5L8.5 7"/>
              </svg>
            </div>
            拓扑处理
          </div>
          <span class="psh-arr">▾</span>
        </div>
        <div v-show="sectionOpen.topo" class="psb">
          <div class="fg">
            <label>节点捕捉容差 (m)</label>
            <input type="number" class="fc" v-model="store.topoTolerance" min="0.01" step="0.5">
          </div>
          <div class="ag" style="padding:0;flex-direction:column;gap:6px;margin-top:6px;">
            <button class="ab ab-blue ab-full" @click="doGenNodes">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 6H10M7.5 3L10 6L7.5 9"/></svg>
              自动生成节点
            </button>
            <div style="display:flex;gap:6px">
              <button class="ab" style="flex:1" @click="doCheckTopo">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 7L4.5 9.5L10 4"/></svg> 拓扑检查
              </button>
            </div>
          </div>
          <!-- 简易结果展示 -->
          <div v-if="store.topoReport" style="margin-top:8px; font-size:11px; padding: 6px; background: #f5f7fa; border-radius: 4px;">
            <div v-if="store.topoReport.ok" style="color: #00a878;">✔ 发现 0 个错误</div>
            <div v-else style="color: #e63946;">✖ 发现 {{ store.topoReport.issues.length }} 个错误</div>
          </div>
        </div>
      </div>
      <!-- 操作日志 -->
      <div class="ps">
        <div class="psh" :class="{ open: logExpanded }" @click="logExpanded = !logExpanded">
          <div class="psh-l">
            <div class="psh-ico" style="background:#f0f4ff;color:#6366f1">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 3h7M2 5.5h7M2 8h4"/>
              </svg>
            </div>
            操作日志
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <span v-if="opLogs.length" style="font-size:10px;background:#6366f1;color:#fff;border-radius:8px;padding:1px 6px;font-weight:700;">{{ opLogs.length }}</span>
            <button
              class="la-btn"
              title="清空日志"
              @click.stop="opLogs = []"
              style="width:18px;height:18px;opacity:0.6"
            >
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 2L8 8M8 2L2 8"/></svg>
            </button>
            <span class="psh-arr">▾</span>
          </div>
        </div>
        <div v-show="logExpanded" class="psb" style="padding:0;">
          <div class="op-log-box">
            <div v-if="opLogs.length === 0" class="op-log-empty">暂无操作记录</div>
            <div
              v-for="entry in opLogs"
              :key="entry.id"
              class="op-log-row"
              :class="`log-${entry.level}`"
            >
              <span class="op-log-time">{{ entry.time }}</span>
              <span class="op-log-dot" :class="`dot-${entry.level}`"></span>
              <span class="op-log-msg">{{ entry.msg }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-show="activeTab === 'props'" class="rp-body">
      <div class="props-empty" v-if="!store.selectedFeature">
        <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
          <path d="M10 6H32L44 18V46H10Z" stroke="#8898b0" stroke-width="2" stroke-linejoin="round"/>
          <path d="M32 6V18H44" stroke="#8898b0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M18 28H34M18 34H28M18 22H26" stroke="#8898b0" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div class="props-empty-text">
          <div class="props-empty-title">未选中任何对象</div>
          <div class="props-empty-desc">切换到<b>选择工具</b><br>单击地图要素查看属性</div>
        </div>
        <button class="ab ab-blue select-mode-btn" @click="enableSelectFromProps">
          启用选择工具
        </button>
      </div>
      <div v-else style="padding: 16px;">
        <h3 style="font-size: 14px; margin-bottom: 8px;">要素属性编辑</h3>
        <p style="font-size: 12px; color: #666; margin-bottom: 2px;">当前选中: {{ store.selectedFeature.type }}</p>
        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">ID: {{ store.selectedFeature.id }}</p>

        <div class="fg" v-for="fd in editableFields" :key="fd.key">
          <label>{{ fd.label }}</label>
          <select v-if="fd.options" v-model="attrForm[fd.key]" class="fc fc-select">
            <option v-for="opt in fd.options" :key="opt" :value="opt">{{ opt }}</option>
          </select>
          <textarea
            v-else-if="fd.multiline"
            v-model="attrForm[fd.key]"
            class="fc"
            rows="3"
          />
          <input
            v-else
            v-model="attrForm[fd.key]"
            class="fc"
            :type="fd.type === 'number' ? 'number' : 'text'"
          >
        </div>

        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <button class="ab ab-blue" style="flex:1" @click="saveAttrs">保存属性</button>
          <button class="ab" style="flex:1" @click="store.selectFeature(null)">清除选择</button>
        </div>

        <div v-if="store.selectedFeature.type === 'section'" style="margin-top: 14px; border-top: 1px solid #e5e7eb; padding-top: 12px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 8px;">
            <h4 style="font-size: 13px; margin: 0;">断面高程表 (R7)</h4>
            <div style="display:flex; gap:6px;">
              <button class="ab" style="min-width:auto; padding:4px 8px;" @click="addSectionProfileRow">新增行</button>
              <button class="ab" style="min-width:auto; padding:4px 8px;" @click="normalizeSectionProfile">排序</button>
            </div>
          </div>

          <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
              <tr>
                <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:6px 4px;">起点距(m)</th>
                <th style="text-align:left; border-bottom:1px solid #e5e7eb; padding:6px 4px;">高程(m)</th>
                <th style="text-align:right; border-bottom:1px solid #e5e7eb; padding:6px 4px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in sectionProfileRows" :key="idx">
                <td style="padding:6px 4px;">
                  <input v-model.number="row.dist" type="number" class="fc" style="padding:4px 6px; font-size:12px;">
                </td>
                <td style="padding:6px 4px;">
                  <input v-model.number="row.elev" type="number" class="fc" style="padding:4px 6px; font-size:12px;">
                </td>
                <td style="padding:6px 4px; text-align:right;">
                  <button class="ab" style="min-width:auto; padding:4px 8px;" @click="removeSectionProfileRow(idx)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="sectionProfileRows.length === 0" style="font-size: 12px; color: #6b7280; margin-top: 6px;">
            暂无断面点，请点击“新增行”录入起点距-高程数据。
          </div>

          <div style="margin-top: 10px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px; padding: 6px;">
            <svg viewBox="0 0 280 120" style="width: 100%; height: 120px; display:block;">
              <rect x="0" y="0" width="280" height="120" fill="#f8fafc" />
              <path v-if="sectionProfileSvgPath" :d="sectionProfileSvgPath" fill="none" stroke="#1a6cff" stroke-width="2" />
              <text v-else x="140" y="64" text-anchor="middle" fill="#94a3b8" font-size="12">至少需要 2 个断面点</text>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Body: 参数 (壳层占位) -->
    <div v-show="activeTab === 'params'" class="rp-body">
       <div class="ps">
        <div class="psh" @click="toggleSection('roughness')">
          <div class="psh-l"><div class="psh-ico" style="background:#fff0e0;color:#d97d45">R</div>糙率参数</div>
        </div>
        <div v-show="sectionOpen.roughness" class="psb">
          <div class="ibox ibox-blue">Manning 糙率 n：天然河道 0.025–0.045，人工渠 0.012–0.025</div>
          <div class="fg-row">
            <div class="fg"><label>主槽 n</label><input v-model.number="computeParams.mainChannelN" type="number" class="fc" step="0.001"></div>
            <div class="fg"><label>时间步长(s)</label><input v-model.number="computeParams.dtSeconds" type="number" class="fc" min="1" step="1"></div>
          </div>
          <div class="fg-row">
            <div class="fg"><label>模拟时长(h)</label><input v-model.number="computeParams.totalHours" type="number" class="fc" min="1" step="1"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Body: 计算 (壳层占位) -->
    <div v-show="activeTab === 'compute'" class="rp-body">
      <div class="ps">
        <div class="psh" @click="toggleSection('runCtrl')">
          <div class="psh-l"><div class="psh-ico" style="background:#e0f7f1;color:#0a9396">▶</div>运行控制</div>
        </div>
        <div v-show="sectionOpen.runCtrl" class="psb">
          <div style="display:flex;gap:7px;margin-bottom:12px">
            <button class="ab ab-teal" style="flex:2" :disabled="computeStatus === 'RUNNING'" @click="startCompute">
              {{ computeStatus === 'RUNNING' ? '计算中...' : '开始计算' }}
            </button>
          </div>
          <div class="prog-top"><span>计算进度（{{ computeStage }}）</span><span>{{ computeProgress }}%</span></div>
          <div class="prog-track"><div class="prog-fill" :style="{ width: `${computeProgress}%` }"></div></div>
          <div style="margin-top:8px;font-size:12px;color:#5c6f86;">状态: {{ computeStatus }}</div>
          <div style="margin-top:8px; border:1px solid #e5e7eb; border-radius:6px; background:#f8fafc; padding:8px; max-height:150px; overflow:auto;">
            <div v-if="computeLogs.length === 0" style="font-size:12px;color:#94a3b8;">暂无日志，点击“开始计算”启动任务。</div>
            <div v-for="(line, idx) in computeLogs" :key="idx" style="font-size:12px; color:#334155; line-height:1.5;">
              {{ line }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Right Panel Base */
.rpanel {
  width: 320px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 200;
  flex-shrink: 0;
}

/* Tabs */
.rp-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  background: var(--bg-secondary);
}
.rp-tab {
  flex: 1;
  padding: 10px 4px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .2px;
  cursor: pointer;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all .15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.rp-tab:hover { color: var(--color-accent); background: rgba(0,212,255,0.12); }
.rp-tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }

/* Body Area */
.rp-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* Panels */
.ps { border-bottom: 1px solid var(--border-color); }
.ps:last-child { border-bottom: none; }
.psh {
  padding: 9px 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  background: var(--bg-tertiary);
  font-size: 10.5px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
}
.psh:hover { background: rgba(0,212,255,0.08); }
.psh-l { display: flex; align-items: center; gap: 7px; }
.psh-ico {
  width: 20px; height: 20px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.psh-arr { transition: transform .18s; font-size: 9px; opacity: .5; }
.psh.open .psh-arr { transform: rotate(180deg); }
.psb { padding: 13px; display: block; }

/* Stats Row */
.stats-row { display: flex; gap: 7px; padding: 12px 13px; }
.sc {
  flex: 1; padding: 10px 8px; background: var(--bg-tertiary);
  border-radius: 8px; text-align: center; border: 1px solid var(--border-color);
  transition: all .15s;
}
.sc:hover { border-color: var(--color-primary); transform: translateY(-1px); box-shadow: 0 1px 3px rgba(13,17,23,.18); }
.sc-val { font-size: 20px; font-weight: 700; color: var(--color-primary); line-height: 1; font-variant-numeric: tabular-nums; }
.sc-lbl { font-size: 10px; color: var(--text-tertiary); margin-top: 4px; text-transform: uppercase; letter-spacing: .5px; }

/* Layer sublist */
.li-expand-arrow {
  font-size: 9px;
  opacity: 0.5;
  margin-left: 3px;
}
.li-sublist {
  list-style: none;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}
.li-sublist ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.li-sub-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 13px 5px 28px;
  font-size: 11.5px;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: background .12s;
}
.li-sub-item:hover {
  background: rgba(24,144,255,.14);
  color: var(--color-primary);
}
.li-sub-item svg { flex-shrink: 0; opacity: 0.5; }
.li-sub-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.li-sub-meta { font-size: 10px; color: var(--text-tertiary); flex-shrink: 0; }
.li-sub-empty {
  padding: 6px 13px 6px 28px;
  font-size: 11px;
  color: var(--text-tertiary);
  font-style: italic;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

/* Operation Log */
.op-log-box {
  max-height: 180px;
  overflow-y: auto;
  padding: 4px 0;
  font-size: 11px;
  scrollbar-width: thin;
}
.op-log-empty {
  padding: 12px 13px;
  color: var(--text-tertiary);
  font-style: italic;
  text-align: center;
}
.op-log-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 4px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  line-height: 1.4;
  transition: background .1s;
}
.op-log-row:hover { background: rgba(255,255,255,0.04); }
.op-log-time {
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  flex-shrink: 0;
  padding-top: 1px;
}
.op-log-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 4px;
}
.dot-info    { background: #64748b; }
.dot-success { background: #00a878; }
.dot-warn    { background: #f4a261; }
.dot-error   { background: #e63946; }
.op-log-msg { color: var(--text-primary); flex: 1; word-break: break-all; }
.log-warn .op-log-msg   { color: #f4a261; }
.log-error .op-log-msg  { color: #e63946; }
.log-success .op-log-msg { color: #00a878; }

/* Layer List */
.layer-list { list-style: none; margin: 0; padding: 0; }
.li {
  display: flex; align-items: center; padding: 8px 13px; gap: 9px;
  border-bottom: 1px solid var(--border-color); transition: background .13s;
}
.li:last-child { border-bottom: none; }
.li:hover { background: rgba(0,212,255,0.08); }
.li-cb { width: 14px; height: 14px; cursor: pointer; accent-color: var(--color-primary); flex-shrink: 0; }
.li-sw { width: 4px; border-radius: 2px; align-self: stretch; flex-shrink: 0; min-height: 28px; }
.li-info { flex: 1; min-width: 0; }
.li-name { font-size: 12px; font-weight: 600; color: var(--text-primary); }
.li-meta { font-size: 11px; color: var(--text-tertiary); margin-top: 1px; }
.la { display: flex; gap: 3px; opacity: 0; transition: opacity .13s; flex-shrink: 0; }
.li:hover .la { opacity: 1; }
.la-btn {
  width: 22px; height: 22px; border: none; border-radius: 4px; cursor: pointer;
  background: rgba(255,255,255,.08); display: flex; align-items: center; justify-content: center;
  transition: all .13s; color: #2d3f55;
}
.la-btn:hover { background: rgba(24,144,255,.18); color: var(--color-primary); }
.la-btn.del:hover { background: #fde8ea; color: #e63946; }

/* Forms */
.fg { margin-bottom: 11px; }
.fg:last-child { margin-bottom: 0; }
.fg label { display: block; font-size: 11px; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; }
.fg-row { display: flex; gap: 8px; }
.fg-row .fg { flex: 1; }
.fc {
  width: 100%; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 6px;
  font-size: 12.5px; background: var(--bg-primary); color: var(--text-primary); transition: all .15s;
}
.fc:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(24,144,255,.18); }

.fc-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding-right: 32px;
  cursor: pointer;
  background-image:
    linear-gradient(45deg, transparent 50%, var(--text-secondary) 50%),
    linear-gradient(135deg, var(--text-secondary) 50%, transparent 50%);
  background-position:
    calc(100% - 16px) calc(50% - 2px),
    calc(100% - 10px) calc(50% - 2px);
  background-size: 6px 6px, 6px 6px;
  background-repeat: no-repeat;
}

.fc-select:hover {
  border-color: var(--color-accent);
}

.fc-select option {
  color: #0d1117;
}

/* Buttons */
.ag { display: flex; flex-wrap: wrap; }
.ab {
  flex: 1; min-width: 100px; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 6px;
  background: var(--bg-primary); color: var(--text-secondary); cursor: pointer; font-size: 12px; font-weight: 500;
  transition: all .15s; display: flex; align-items: center; justify-content: center; gap: 5px;
}
.ab:hover { border-color: var(--color-primary); color: var(--color-primary); background: rgba(24,144,255,.16); }
.ab-blue { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.ab-blue:hover { background: #1250cc; border-color: #1250cc; color: #fff; }
.ab-teal { background: #0a9396; color: #fff; border-color: #0a9396; }
.ab-teal:hover { background: #077880; color: #fff; border-color: #077880; }
.ab-full { width: 100%; flex: unset; min-width: unset; }

.props-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  flex: 1; color: var(--text-tertiary); text-align: center;
}

.props-empty-text {
  margin-top: 12px;
}

.props-empty-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.props-empty-desc {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-tertiary);
}

.select-mode-btn {
  margin-top: 10px;
  flex: 0 0 auto;
  align-self: center;
  display: inline-flex;
  justify-content: center;
  width: auto;
  min-width: 140px;
  padding: 6px 14px;
}

.prog-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary);
}

.prog-track {
  margin-top: 6px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,.12);
  overflow: hidden;
}

.prog-fill {
  height: 100%;
  background: linear-gradient(90deg, #0a9396, #1a6cff);
  transition: width 0.4s ease;
}
</style>
