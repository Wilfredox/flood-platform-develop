<script setup lang="ts">
/**
 * R1DMap.vue — River1D 地图区域
 * R2: Leaflet 地图 + 天地图矢量/影像切换 + 坐标栏
 * R3: 河道/岸线/断面/建筑物 绘制交互 + 捕捉环 + 顶部绘制提示
 */
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRiver1dStore } from '@/stores/useRiver1dStore'
import type { LatLng, River, Bank, CrossSection, Structure } from '@/types/river1d'

// ── 天地图 Key（与大屏共用） ───────────────────────────
const TDT_KEY = 'b83bce392f5afe6e092f7d2a11e42d3b'
const DEFAULT_CENTER: [number, number] = [29.13984534608853, 120.43074147503992]
const DEFAULT_ZOOM = 10
const DEFAULT_FOCUS_BOUNDS: [[number, number], [number, number]] = [
  [29.194344444444444, 120.34602777777778],
  [29.046411111111112, 120.57168055555556]
]

const CRS_OPTIONS = [
  { value: 'WGS84', label: 'WGS84 地理坐标' },
  { value: 'CGCS2000_3TM_108', label: 'CGCS2000 3°带 / 108°E' },
  { value: 'CGCS2000_3TM_111', label: 'CGCS2000 3°带 / 111°E' },
  { value: 'CGCS2000_3TM_114', label: 'CGCS2000 3°带 / 114°E' },
  { value: 'CGCS2000_3TM_117', label: 'CGCS2000 3°带 / 117°E' },
  { value: 'CGCS2000_3TM_120', label: 'CGCS2000 3°带 / 120°E' },
  { value: 'CGCS2000_3TM_123', label: 'CGCS2000 3°带 / 123°E' }
]

// ── 底图配置 ──────────────────────────────────────────
const BASEMAPS = [
  {
    id: 0, label: '天地图矢量',
    url: `https://t{s}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${TDT_KEY}`,
    ann: `https://t{s}.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${TDT_KEY}`,
  },
  {
    id: 1, label: '天地图影像',
    url: `https://t{s}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${TDT_KEY}`,
    ann: `https://t{s}.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${TDT_KEY}`,
  },
]

const store = useRiver1dStore()
const mapEl = ref<HTMLDivElement | null>(null)
const coordX = ref('—')
const coordY = ref('—')
const coordLabelX = ref('经度')
const coordLabelY = ref('纬度')
const coordZ = ref('1')
const coordGeoDms = ref('—')
const activeBm = ref(1)
const selectedCrs = ref(store.project.crs || 'CGCS2000_3TM_120')
const crsDisplayLabel = computed(() => {
  const found = CRS_OPTIONS.find(x => x.value === selectedCrs.value)
  return found ? found.label : selectedCrs.value
})

// 绘制提示
const drawHint = ref('')
const drawHintVisible = ref(false)
let lastMouseLatLng: LatLng | null = null

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let L: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let map: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let bmLayers: any[] = []
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let annLayer: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let lg: Record<string, any> = {}

// 绘制状态
let drawPts: LatLng[] = []
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let tempLine: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let snapRingEl: HTMLDivElement | null = null

// 要素 Leaflet 图层映射（id → leaflet layer）
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const featureLayerMap = new Map<string, any>()
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let nodeEditHandles: any[] = []

function getLayerKey(type: 'river' | 'bank' | 'section' | 'structure', id: string): string {
  return `${type}:${id}`
}

// 样式常量
const LSTYLE: Record<string, object> = {
  river:     { color: '#1a6cff', weight: 3,   opacity: 0.9 },
  bank:      { color: '#00a878', weight: 2.5, opacity: 0.9, dashArray: '10 5' },
  section:   { color: '#f4a261', weight: 2.5, opacity: 1.0, dashArray: '10 4' },
  structure: { color: '#e63946', weight: 3.5, opacity: 1.0 },
}

function applyCursorByTool(tool: string) {
  if (!map) return
  const mapContainer = map.getContainer() as HTMLElement
  const cursorByTool: Record<string, string> = {
    select: "url('/cursors/select.svg') 3 3, pointer",
    river: "url('/cursors/Riverway.svg') 4 4, crosshair",
    bank: "url('/cursors/water_front.svg') 6 22, crosshair",
    section: "url('/cursors/fracture_surface.svg') 6 8, crosshair",
    structure: "url('/cursors/construction.svg') 4 4, crosshair",
    node: "url('/cursors/node.svg') 12 12, move"
  }
  const cursor = cursorByTool[tool] || 'default'
  mapContainer.style.cursor = cursor
  const panes = mapContainer.querySelectorAll('.leaflet-pane, .leaflet-interactive')
  panes.forEach((el) => ((el as HTMLElement).style.cursor = cursor))
}

function keepCursorByTool() {
  applyCursorByTool(store.activeTool)
}

function distPointToSegmentPx(
  px: number,
  py: number,
  ax: number,
  ay: number,
  bx: number,
  by: number
): number {
  const abx = bx - ax
  const aby = by - ay
  const len2 = abx * abx + aby * aby
  if (len2 < 1e-6) {
    return Math.hypot(px - ax, py - ay)
  }
  let t = ((px - ax) * abx + (py - ay) * aby) / len2
  t = Math.max(0, Math.min(1, t))
  const cx = ax + t * abx
  const cy = ay + t * aby
  return Math.hypot(px - cx, py - cy)
}

function selectNearestFeature(lat: number, lng: number) {
  if (!map || !L) return
  const clickPt = map.latLngToLayerPoint(L.latLng(lat, lng))
  const tolerancePx = 10
  let best: { d: number; feature: River | Bank | CrossSection | Structure } | null = null

  const tryLineFeature = (coords: LatLng[], feature: River | Bank | CrossSection | Structure) => {
    for (let i = 1; i < coords.length; i++) {
      const a = map.latLngToLayerPoint(L.latLng(coords[i - 1].lat, coords[i - 1].lng))
      const b = map.latLngToLayerPoint(L.latLng(coords[i].lat, coords[i].lng))
      const d = distPointToSegmentPx(clickPt.x, clickPt.y, a.x, a.y, b.x, b.y)
      if (d <= tolerancePx && (!best || d < best.d)) {
        best = { d, feature }
      }
    }
  }

  store.rivers.forEach((r) => {
    r.reaches.forEach((rc) => tryLineFeature(rc.coords, r))
  })
  store.banks.forEach((b) => tryLineFeature(b.coords, b))
  store.sections.forEach((s) => tryLineFeature(s.coords, s))
  store.structures.forEach((s) => tryLineFeature(s.coords, s))

  store.selectFeature(best ? best.feature : null)
}

function getCentralMeridian(crs: string): number | null {
  const cmMap: Record<string, number> = {
    CGCS2000_3TM_108: 108,
    CGCS2000_3TM_111: 111,
    CGCS2000_3TM_114: 114,
    CGCS2000_3TM_117: 117,
    CGCS2000_3TM_120: 120,
    CGCS2000_3TM_123: 123
  }
  return cmMap[crs] ?? null
}

function ll2gk3(lng: number, lat: number, cm: number): { x: number; y: number } {
  const a = 6378137
  const f = 1 / 298.257222101
  const b = a * (1 - f)
  const e2 = 1 - (b / a) ** 2
  const ep2 = e2 / (1 - e2)
  const phi = (lat * Math.PI) / 180
  const n = a / Math.sqrt(1 - e2 * Math.sin(phi) ** 2)
  const t = Math.tan(phi) ** 2
  const c = ep2 * Math.cos(phi) ** 2
  const aa = ((lng - cm) * Math.PI) / 180 * Math.cos(phi)
  const m = a * (
    (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * phi
      - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * Math.sin(2 * phi)
      + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * Math.sin(4 * phi)
      - (35 * e2 ** 3 / 3072) * Math.sin(6 * phi)
  )

  return {
    x: n * (aa + (1 - t + c) * aa ** 3 / 6 + (5 - 18 * t + t * t + 72 * c - 58 * ep2) * aa ** 5 / 120) + 500000,
    y: m + n * Math.tan(phi) * (aa * aa / 2 + (5 - t + 9 * c + 4 * c * c) * aa ** 4 / 24)
  }
}

function toDms(value: number): { d: number; m: number; s: string } {
  const absValue = Math.abs(value)
  const d = Math.floor(absValue)
  const minuteFull = (absValue - d) * 60
  const m = Math.floor(minuteFull)
  const s = ((minuteFull - m) * 60).toFixed(2)
  return { d, m, s }
}

function formatLatLngDms(lat: number, lng: number): string {
  const latDms = toDms(lat)
  const lngDms = toDms(lng)
  return `${latDms.d}° ${latDms.m}' ${latDms.s}" ${lat >= 0 ? '北' : '南'}  ${lngDms.d}° ${lngDms.m}' ${lngDms.s}" ${lng >= 0 ? '东' : '西'}`
}

function updateCoordDisplay(lat: number, lng: number) {
  coordGeoDms.value = formatLatLngDms(lat, lng)

  if (selectedCrs.value === 'WGS84') {
    coordLabelX.value = '经度'
    coordLabelY.value = '纬度'
    coordX.value = lng.toFixed(6)
    coordY.value = lat.toFixed(6)
    return
  }

  const cm = getCentralMeridian(selectedCrs.value)
  if (!cm) {
    coordLabelX.value = '经度'
    coordLabelY.value = '纬度'
    coordX.value = lng.toFixed(6)
    coordY.value = lat.toFixed(6)
    return
  }

  const xy = ll2gk3(lng, lat, cm)
  coordLabelX.value = 'X(东)'
  coordLabelY.value = 'Y(北)'
  coordX.value = xy.x.toFixed(1)
  coordY.value = xy.y.toFixed(1)
}

// ── 初始化 ────────────────────────────────────────────
onMounted(async () => {
  // 动态加载 Leaflet（已在 index.html 或通过 CDN 引入）
  // @ts-ignore
  L = window.L
  if (!L) {
    console.error('Leaflet not loaded')
    return
  }

  map = L.map(mapEl.value, {
    center: DEFAULT_CENTER,
    zoom: DEFAULT_ZOOM,
    zoomControl: false,
    attributionControl: true,
  })

  map.fitBounds(DEFAULT_FOCUS_BOUNDS, { padding: [0, 0], animate: false })

  // 初始化底图
  initBasemaps()

  // 图层组
  const layerKeys = ['river', 'bank', 'section', 'structure', 'nodes']
  layerKeys.forEach(k => {
    lg[k] = L.layerGroup().addTo(map)
  })

  // 坐标追踪
  map.on('mousemove', (e: any) => {
    keepCursorByTool()
    lastMouseLatLng = { lat: e.latlng.lat, lng: e.latlng.lng }
    updateCoordDisplay(e.latlng.lat, e.latlng.lng)
    coordZ.value = String(map.getZoom())

    // 更新临时线
    if (drawPts.length > 0 && store.activeTool !== 'select') {
      const pts = [...drawPts, { lat: e.latlng.lat, lng: e.latlng.lng }]
      if (tempLine) {
        tempLine.setLatLngs(pts.map(p => L.latLng(p.lat, p.lng)))
      }
    }
  })

  // 点击绘制
  map.on('click', (e: any) => {
    if (store.activeTool === 'select') {
      selectNearestFeature(e.latlng.lat, e.latlng.lng)
      return
    }
    if (store.activeTool === 'node') {
      selectNearestFeature(e.latlng.lat, e.latlng.lng)
      return
    }
    const pt: LatLng = { lat: e.latlng.lat, lng: e.latlng.lng }

    // 断面/建筑物：只需2点，第2次点击即完成
    if ((store.activeTool === 'section' || store.activeTool === 'structure') && drawPts.length === 1) {
      drawPts.push(pt)
      finishDraw()
      return
    }

    drawPts.push(pt)

    if (!tempLine) {
      tempLine = L.polyline(
        drawPts.map(p => L.latLng(p.lat, p.lng)),
        { color: LSTYLE[store.activeTool] ? (LSTYLE[store.activeTool] as any).color : '#aaa', weight: 2, opacity: 0.7, dashArray: '6 3' }
      ).addTo(map)
    }

    showHint()
  })

  // 双击结束（河道/岸线）
  map.on('dblclick', (e: any) => {
    if (store.activeTool === 'select') return
    if (store.activeTool === 'section' || store.activeTool === 'structure') return
    L.DomEvent.stopPropagation(e)
    if (drawPts.length >= 2) finishDraw()
  })

  // ESC 取消
  window.addEventListener('keydown', onKeyDown)
  map.on('mousedown', keepCursorByTool)
  map.on('mouseup', keepCursorByTool)
  map.on('dragstart', keepCursorByTool)
  map.on('drag', keepCursorByTool)
  map.on('dragend', keepCursorByTool)
  map.on('zoomstart', keepCursorByTool)
  map.on('zoomend', keepCursorByTool)

  // 监听图层可见性
  watchLayers()

  keepCursorByTool()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeyDown)
  if (map) map.remove()
})

watch(selectedCrs, (value) => {
  store.project.crs = value
  if (lastMouseLatLng) {
    updateCoordDisplay(lastMouseLatLng.lat, lastMouseLatLng.lng)
  }
})

// ── 底图 ──────────────────────────────────────────────
function initBasemaps() {
  const bm = BASEMAPS[activeBm.value]
  bmLayers = BASEMAPS.map(b => L.tileLayer(b.url, { subdomains: ['0','1','2','3','4','5','6','7'], maxZoom: 18, tileSize: 256 }))
  bmLayers[activeBm.value].addTo(map)
  // 注记层
  if (bm.ann) {
    annLayer = L.tileLayer(bm.ann, { subdomains: ['0','1','2','3','4','5','6','7'], maxZoom: 18, tileSize: 256 })
    annLayer.addTo(map)
  }
}

function switchBm(idx: number) {
  if (idx === activeBm.value) return
  bmLayers[activeBm.value]?.remove()
  annLayer?.remove()
  activeBm.value = idx
  bmLayers[idx]?.addTo(map)
  const bm = BASEMAPS[idx]
  if (bm.ann) {
    annLayer = L.tileLayer(bm.ann, { subdomains: ['0','1','2','3','4','5','6','7'], maxZoom: 18, tileSize: 256 })
    annLayer.addTo(map)
  } else {
    annLayer = null
  }
}

// ── 工具光标 ──────────────────────────────────────────
watch(() => store.activeTool, (tool) => {
  if (!map) return
  applyCursorByTool(tool)
  if (tool === 'select') {
    hideHint()
  } else {
    showHint()
  }
  // 取消正在绘制的内容
  cancelCurrentDraw()
  renderNodeHandles()
}, { immediate: true })

watch(() => store.selectedFeature, () => {
  renderNodeHandles()
})

// ── 图层可见性监听 ────────────────────────────────────
function watchLayers() {
  watch(() => store.layerVisible, (vis) => {
    Object.keys(vis).forEach(k => {
      if (!lg[k]) return
      if (vis[k]) { if (!map.hasLayer(lg[k])) lg[k].addTo(map) }
      else { map.removeLayer(lg[k]) }
    })
  }, { deep: true })
}

// ── 绘制提示 ──────────────────────────────────────────
const HINTS: Record<string, string> = {
  river:     '点击添加节点，双击结束绘制',
  bank:      '点击添加节点，双击结束绘制',
  section:   '点击起点，再点终点完成断面绘制',
  structure: '点击起点，再点终点完成建筑物绘制',
  node:      '拖拽白色节点可修改当前选中线要素',
}
function showHint() {
  drawHint.value = HINTS[store.activeTool] || ''
  drawHintVisible.value = !!drawHint.value
}
function hideHint() {
  drawHintVisible.value = false
}

// ── 完成绘制 ──────────────────────────────────────────
function finishDraw() {
  if (drawPts.length < 2) { cancelCurrentDraw(); return }
  const pts = [...drawPts]

  // 清除临时线
  if (tempLine) { map.removeLayer(tempLine); tempLine = null }
  drawPts = []

  const tool = store.activeTool

  // 写入 store 并获得新要素
  let feature: River | Bank | CrossSection | Structure

  if (tool === 'river') {
    feature = store.addRiver(pts)
    const pl = L.polyline(pts.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE.river }).addTo(lg.river)
    pl.on('click', (e: any) => {
      L.DomEvent.stopPropagation(e)
      if (store.activeTool === 'select') store.selectFeature(feature)
    })
    const reachId = feature.reaches[0]?.id
    if (reachId) {
      featureLayerMap.set(getLayerKey('river', reachId), pl)
    }
  } else if (tool === 'bank') {
    feature = store.addBank(pts)
    const pl = L.polyline(pts.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE.bank }).addTo(lg.bank)
    pl.on('click', (e: any) => {
      L.DomEvent.stopPropagation(e)
      if (store.activeTool === 'select') store.selectFeature(feature)
    })
    featureLayerMap.set(getLayerKey('bank', feature.id), pl)
  } else if (tool === 'section') {
    feature = store.addSection(pts)
    const pl = L.polyline(pts.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE.section }).addTo(lg.section)
    pl.on('click', (e: any) => {
      L.DomEvent.stopPropagation(e)
      if (store.activeTool === 'select') store.selectFeature(feature)
    })
    featureLayerMap.set(getLayerKey('section', feature.id), pl)
  } else if (tool === 'structure') {
    feature = store.addStructure(pts)
    const pl = L.polyline(pts.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE.structure }).addTo(lg.structure)
    pl.on('click', (e: any) => {
      L.DomEvent.stopPropagation(e)
      if (store.activeTool === 'select') store.selectFeature(feature)
    })
    featureLayerMap.set(getLayerKey('structure', feature.id), pl)
  }

  hideHint()
}

// ── 取消绘制 ──────────────────────────────────────────
function cancelCurrentDraw() {
  if (tempLine) { map.removeLayer(tempLine); tempLine = null }
  drawPts = []
  hideHint()
}

// ── 键盘快捷键（仅保留 ESC 取消绘制，工具切换快捷键已移除）────
function onKeyDown(e: KeyboardEvent) {
  if (e.code === 'Escape') cancelCurrentDraw()
}

function calcLineLength(coords: LatLng[]): number {
  let total = 0
  for (let i = 1; i < coords.length; i++) {
    const a = coords[i - 1]
    const b = coords[i]
    const R = 6371000
    const phi1 = a.lat * Math.PI / 180
    const phi2 = b.lat * Math.PI / 180
    const dPhi = (b.lat - a.lat) * Math.PI / 180
    const dLambda = (b.lng - a.lng) * Math.PI / 180
    const x = Math.sin(dPhi / 2) ** 2 + Math.cos(phi1) * Math.cos(phi2) * Math.sin(dLambda / 2) ** 2
    total += 2 * R * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x))
  }
  return Math.round(total)
}

function clearNodeHandles() {
  nodeEditHandles.forEach((m) => map?.removeLayer(m))
  nodeEditHandles = []
}

function getEditableCoords(target: River | Bank | CrossSection | Structure): LatLng[] {
  if (target.type === 'river') {
    return target.reaches[0]?.coords || []
  }
  return target.coords
}

function getFeatureLayerKey(target: River | Bank | CrossSection | Structure): string | null {
  if (target.type === 'river') {
    const rid = target.reaches[0]?.id
    return rid ? getLayerKey('river', rid) : null
  }
  return getLayerKey(target.type, target.id)
}

function syncEditedFeature(target: River | Bank | CrossSection | Structure, coords: LatLng[]) {
  const key = getFeatureLayerKey(target)
  if (key) {
    const layer = featureLayerMap.get(key)
    if (layer) {
      layer.setLatLngs(coords.map((p) => L.latLng(p.lat, p.lng)))
    }
  }
  if (target.type === 'river') target.attrs.length = calcLineLength(coords)
  if (target.type === 'bank') target.attrs.length = calcLineLength(coords)
  store.isDirty = true
}

function renderNodeHandles() {
  clearNodeHandles()
  if (!map || !L) return
  if (store.activeTool !== 'node') return
  if (!store.selectedFeature) return

  const selected = store.selectedFeature
  const coords = getEditableCoords(selected)
  if (coords.length < 2) return

  coords.forEach((pt, idx) => {
    const marker = L.marker([pt.lat, pt.lng], {
      draggable: true,
      icon: L.divIcon({
        className: 'r1d-node-handle',
        html: '<span class="r1d-node-handle-dot"></span>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      })
    }).addTo(map)

    marker.on('click', (e: any) => L.DomEvent.stopPropagation(e))
    marker.on('dragstart', () => keepCursorByTool())
    marker.on('drag', (e: any) => {
      const ll = e.target.getLatLng()
      coords[idx] = { lat: ll.lat, lng: ll.lng }
      syncEditedFeature(selected, coords)
      keepCursorByTool()
    })
    marker.on('dragend', () => {
      syncEditedFeature(selected, coords)
      keepCursorByTool()
    })

    nodeEditHandles.push(marker)
  })
}

// ── 全图缩放 ──────────────────────────────────────────
function fitAll() {
  if (!map) return
  const allPts: LatLng[] = []
  store.rivers.forEach(r => r.reaches.forEach(rc => allPts.push(...rc.coords)))
  store.banks.forEach(b => allPts.push(...b.coords))
  store.sections.forEach(s => allPts.push(...s.coords))
  store.structures.forEach(s => allPts.push(...s.coords))
  if (allPts.length >= 2) {
    const bounds = L.latLngBounds(allPts.map((p: LatLng) => L.latLng(p.lat, p.lng)))
    map.fitBounds(bounds, { padding: [40, 40] })
  }
}

// ── 渲染节点（R5） ────────────────────────────────────
function renderNodes() {
  lg.nodes.clearLayers()
  const st = store.nodeStyle
  store.nodes.forEach(nd => {
    const color = nd.nodeType === 'upstream' ? st.colorUpstream
                : nd.nodeType === 'junction' ? st.colorJunction
                : st.colorDownstream
    L.circleMarker([nd.lat, nd.lng], {
      radius: st.radius,
      fillColor: color,
      color: '#fff',
      weight: 1.5,
      fillOpacity: 1,
    }).bindTooltip(nd.id, { permanent: st.showLabel, direction: 'top', offset: [0, -4], className: 'r1d-node-label' }).addTo(lg.nodes)
  })
}

// ── 撤销时同步删除地图图层 ────────────────────────────
watch(() => store.rivers.length + store.banks.length + store.sections.length + store.structures.length,
  () => {
    // 重绘所有非河道图层（简单同步）
    ;['bank','section','structure'].forEach(type => {
      lg[type]?.clearLayers()
      const arr = type === 'bank' ? store.banks : type === 'section' ? store.sections : store.structures
      arr.forEach((f: any) => {
        const existing = featureLayerMap.get(getLayerKey(type as 'bank' | 'section' | 'structure', f.id))
        if (!existing) {
          const pl = L.polyline(f.coords.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE[type] })
          pl.on('click', (e: any) => {
            L.DomEvent.stopPropagation(e)
            if (store.activeTool === 'select') store.selectFeature(f)
          })
          pl.addTo(lg[type])
          featureLayerMap.set(getLayerKey(type as 'bank' | 'section' | 'structure', f.id), pl)
        } else {
          existing.addTo(lg[type])
        }
      })
    })
    // 河道
    lg.river?.clearLayers()
    store.rivers.forEach((r: River) => {
      r.reaches.forEach(rc => {
        const existing = featureLayerMap.get(getLayerKey('river', rc.id))
        if (!existing) {
          const pl = L.polyline(rc.coords.map((p: LatLng) => L.latLng(p.lat, p.lng)), { ...LSTYLE.river })
          pl.on('click', (e: any) => {
            L.DomEvent.stopPropagation(e)
            if (store.activeTool === 'select') store.selectFeature(r)
          })
          pl.addTo(lg.river)
          featureLayerMap.set(getLayerKey('river', rc.id), pl)
        } else {
          existing.addTo(lg.river)
        }
      })
    })
    renderNodeHandles()
  }
)

// ── 飞行到指定坐标（供图层列表点击使用）─────────────────
function flyToCoords(coords: LatLng[]) {
  if (!map || !L || coords.length === 0) return
  if (coords.length === 1) {
    map.setView([coords[0].lat, coords[0].lng], 14, { animate: true })
  } else {
    const bounds = L.latLngBounds(coords.map((p: LatLng) => L.latLng(p.lat, p.lng)))
    map.fitBounds(bounds, { padding: [60, 60], animate: true })
  }
}

// 暴露给父组件
defineExpose({ fitAll, cancelCurrentDraw, renderNodes, switchBm, flyToCoords })
</script>

<template>
  <div class="r1d-map-wrap">
    <!-- 地图容器 -->
    <div ref="mapEl" class="r1d-map-container" />

    <!-- 绘制提示条 -->
    <Transition name="hint-fade">
      <div v-if="drawHintVisible" class="draw-hint">
        <span class="dh-dot" />
        <span>{{ drawHint }}</span>
        <span class="dh-key">双击</span>结束&nbsp;·&nbsp;<span class="dh-key">ESC</span>取消
      </div>
    </Transition>

    <!-- 底图切换 -->
    <div class="bm-switcher">
      <button
        v-for="bm in BASEMAPS"
        :key="bm.id"
        class="bm-btn"
        :class="{ active: activeBm === bm.id }"
        @click="switchBm(bm.id)"
      >{{ bm.label }}</button>
    </div>

    <!-- 地图控制按钮 -->
    <div class="map-fabs">
      <button class="fab" title="放大" @click="map?.zoomIn()">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M7 3V11M3 7H11"/>
        </svg>
      </button>
      <button class="fab" title="缩小" @click="map?.zoomOut()">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M3 7H11"/>
        </svg>
      </button>
    </div>

    <!-- 坐标栏 -->
    <div class="coord-bar">
      <div class="cb-item"><span class="cb-l">{{ coordLabelX }}</span><span class="cb-v">{{ coordX }}</span></div>
      <span class="cb-sep">|</span>
      <div class="cb-item"><span class="cb-l">{{ coordLabelY }}</span><span class="cb-v">{{ coordY }}</span></div>
      <span class="cb-sep">|</span>
      <div class="cb-item"><span class="cb-l">经纬</span><span class="cb-v cb-geo">{{ coordGeoDms }}</span></div>
      <span class="cb-sep">|</span>
      <div class="cb-item"><span class="cb-l">缩放</span><span class="cb-v">{{ coordZ }}</span></div>
      <select v-model="selectedCrs" class="coord-crs-select">
        <option v-for="item in CRS_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</option>
      </select>
      <span class="coord-crs">{{ crsDisplayLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.r1d-map-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.r1d-map-container {
  width: 100%;
  height: 100%;
  background: #d4e3ec;
}

/* 绘制提示 */
.draw-hint {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 500;
  background: rgba(13,17,23,.87);
  backdrop-filter: blur(8px);
  color: rgba(255,255,255,.92);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,.1);
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(13,17,23,.3);
}
.dh-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #1a6cff;
  animation: dhpulse 1.2s infinite;
  flex-shrink: 0;
}
@keyframes dhpulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }
.dh-key {
  background: rgba(255,255,255,.15);
  border-radius: 3px;
  padding: 1px 5px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
}
.hint-fade-enter-active, .hint-fade-leave-active { transition: opacity .2s; }
.hint-fade-enter-from, .hint-fade-leave-to { opacity: 0; }

/* 底图切换 */
.bm-switcher {
  position: absolute;
  left: 12px;
  bottom: 36px;
  z-index: 500;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bm-btn {
  padding: 5px 10px;
  border-radius: 5px;
  border: 1px solid rgba(0,0,0,.15);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(6px);
  color: #2d3f55;
  transition: all .15s;
  white-space: nowrap;
}
.bm-btn:hover:not(.active) { background: #fff; color: #1a6cff; }
.bm-btn.active { background: #1a6cff; color: #fff; border-color: #1a6cff; }

/* FABs */
.map-fabs {
  position: absolute;
  right: 12px;
  bottom: 36px;
  z-index: 500;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.fab {
  width: 32px; height: 32px;
  border-radius: 7px; border: none; cursor: pointer;
  background: #fff;
  box-shadow: 0 4px 12px rgba(13,17,23,.12);
  display: flex; align-items: center; justify-content: center;
  color: #2d3f55;
  transition: all .15s;
}
.fab:hover { background: #1a6cff; color: #fff; }

/* 坐标栏 */
.coord-bar {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  z-index: 500;
  background: rgba(13,17,23,.78);
  backdrop-filter: blur(6px);
  padding: 4px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}
.cb-item { display: flex; gap: 5px; align-items: center; }
.cb-l { color: rgba(255,255,255,.35); }
.cb-v { color: rgba(255,255,255,.8); }
.cb-geo { color: rgba(255,255,255,.9); letter-spacing: 0.2px; }
.cb-sep { color: rgba(255,255,255,.12); font-size: 14px; }
.coord-crs { margin-left: 8px; color: rgba(255,255,255,.3); font-size: 10px; }
.coord-crs-select {
  margin-left: auto;
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.2);
  color: rgba(255,255,255,.88);
  border-radius: 4px;
  font-size: 11px;
  height: 22px;
  padding: 0 6px;
}

.coord-crs-select:focus {
  outline: none;
  border-color: rgba(26,108,255,.8);
}

.coord-crs-select option {
  color: #0d1117;
}
</style>

<style>
/* 全局：节点标签 */
.r1d-node-label {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 10px;
  font-weight: 700;
  color: #2d3f55;
  white-space: nowrap;
}

.r1d-node-handle {
  background: transparent !important;
  border: none !important;
}

.r1d-node-handle-dot {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #00c2ff;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, .24);
}
</style>
