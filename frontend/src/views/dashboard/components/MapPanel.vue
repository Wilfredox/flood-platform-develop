<script setup lang="ts">
/**
 * 天地图地图面板 · 南江流域版
 * 主页仅展示南江流域边界和站点，含站点增删改功能
 */
import { ref, onMounted, watch, reactive } from 'vue'
import type { StationInfo } from '@/types/station'

/** 天地图开发者 Key */
const TIANDITU_KEY = 'b83bce392f5afe6e092f7d2a11e42d3b'
const GEOJSON_BASE = __DATASET_GEOJSON_ROUTE__ || '/dataset-geojson'

type BoundaryKind = 'province' | 'city' | 'district'

type BoundarySpec = {
  fileName: string
  label: string
  kind: BoundaryKind
}

const BOUNDARY_SPECS: BoundarySpec[] = [
  { fileName: '浙江省.geojson', label: '浙江省', kind: 'province' },
  { fileName: '金华市.geojson', label: '金华市', kind: 'city' },
  { fileName: '东阳市.geojson', label: '东阳市', kind: 'district' }
]

const props = defineProps<{
  stations: StationInfo[]
  selectedId: string
}>()

const emit = defineEmits<{
  (e: 'select', stationId: string): void
  (e: 'stationsChange', stations: StationInfo[]): void
}>()

// ── 响应式站点列表（支持增删改）─────────────────────────────
const localStations = ref<StationInfo[]>([...props.stations])

const mapContainer = ref<HTMLDivElement>()
let mapInstance: any = null
let boundaryLayer: any = null
let boundaryLabelMarkers: any[] = []
let boundaryBounds: any = null
let provinceBounds: any = null
let imgLayer: any = null
let imgAnnLayer: any = null
let vecLayer: any = null
let vecAnnLayer: any = null
const markers: Record<string, any> = {}

const showBoundary = ref(true)
const basemapMode = ref<'img' | 'vec'>('img')

function getBoundaryStyle(kind: BoundaryKind) {
  if (kind === 'province') {
    return {
      color: '#00D4FF',
      weight: 2,
      fillOpacity: 0
    }
  }
  if (kind === 'city') {
    return {
      color: '#FFD666',
      weight: 2,
      fillColor: '#FFD666',
      fillOpacity: 0.05
    }
  }
  return {
    color: '#52C41A',
    weight: 2,
    fillColor: '#52C41A',
    fillOpacity: 0.12
  }
}

function getBoundaryLabelColor(kind: BoundaryKind): string {
  if (kind === 'province') return '#00D4FF'
  if (kind === 'city') return '#FFD666'
  return '#52C41A'
}

async function fetchGeoJson(fileName: string) {
  const encodedFileName = encodeURIComponent(fileName)
  const response = await fetch(`${GEOJSON_BASE}/${encodedFileName}`)
  if (!response.ok) {
    throw new Error(`加载边界文件失败: ${fileName}`)
  }
  return response.json()
}

function showBoundaryLabels() {
  if (!mapInstance) return
  boundaryLabelMarkers.forEach((marker) => marker.addTo(mapInstance))
}

function hideBoundaryLabels() {
  boundaryLabelMarkers.forEach((marker) => marker.remove())
}

async function initBoundaryLayers(L: any) {
  if (!mapInstance) return

  boundaryLabelMarkers = []
  boundaryBounds = null
  provinceBounds = null
  const layerGroup = L.featureGroup()

  for (const spec of BOUNDARY_SPECS) {
    const geojson = await fetchGeoJson(spec.fileName)
    const geoLayer = L.geoJSON(geojson as any, {
      style: () => getBoundaryStyle(spec.kind),
      onEachFeature: (feature: any, layer: any) => {
        const name = feature.properties?.name || spec.label
        layer.bindPopup(`
          <div style="font-size:13px;line-height:1.7;min-width:130px;padding:2px 0">
            <b style="color:${getBoundaryLabelColor(spec.kind)}">${name}</b><br/>
            <span style="color:#8BA3C7;font-size:11px">数据源：${spec.fileName}</span>
          </div>
        `, { maxWidth: 240 })
      }
    })

    geoLayer.addTo(layerGroup)
    const layerBounds = geoLayer.getBounds()
    if (layerBounds?.isValid()) {
      if (spec.kind === 'province') {
        provinceBounds = layerBounds
      }
      boundaryBounds = boundaryBounds ? boundaryBounds.extend(layerBounds) : layerBounds
      const center = layerBounds.getCenter()
      const labelMarker = L.marker(center, {
        icon: L.divIcon({
          className: '',
          html: `<span style="
            color: ${getBoundaryLabelColor(spec.kind)};
            font-size: 12px;
            font-weight: 700;
            text-shadow: 0 0 6px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,0.9);
            white-space: nowrap;
            pointer-events: none;
            letter-spacing: 0.5px;
          ">${spec.label}</span>`,
          iconSize: [0, 0],
          iconAnchor: [0, 0]
        }),
        interactive: false
      })
      boundaryLabelMarkers.push(labelMarker)
    }
  }

  boundaryLayer = layerGroup.addTo(mapInstance)
  showBoundaryLabels()

  if (provinceBounds?.isValid()) {
    mapInstance.fitBounds(provinceBounds, {
      padding: [28, 28],
      animate: false,
      maxZoom: 8
    })
  }
}

// ── 站点管理面板状态 ──────────────────────────────────────────
const showManagePanel = ref(false)
const showStationDialog = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('新增站点')

const stationForm = reactive<StationInfo>({
  id: '', name: '', basinId: 'basin-nanjiang', basinName: '南江流域',
  type: 'water_level', lng: 120.483, lat: 29.050, status: 'online'
})

const formError = ref('')

function getStatusColor(status: string): string {
  switch (status) {
    case 'warning': return '#FAAD14'
    case 'offline': return '#F5222D'
    default: return '#1890FF'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'warning': return '预警'
    case 'offline': return '离线'
    default: return '正常'
  }
}

function getTypeLabel(type: string): string {
  switch (type) {
    case 'water_level': return '水位站'
    case 'rainfall': return '雨量站'
    case 'flow': return '流量站'
    default: return type
  }
}

// ── 地图标记管理 ──────────────────────────────────────────────
function createMarkerIcon(stn: StationInfo, L: any) {
  const color = getStatusColor(stn.status)
  const isSelected = stn.id === props.selectedId
  const size = isSelected ? 20 : 16
  const shadow = isSelected
    ? `0 0 0 3px rgba(255,255,255,0.5), 0 0 16px ${color}`
    : `0 0 12px ${color}`

  return L.divIcon({
    className: '',
    html: `<div style="
      width: ${size}px; height: ${size}px;
      background: ${color};
      border: 2px solid rgba(255,255,255,0.85);
      border-radius: 50%;
      box-shadow: ${shadow};
      cursor: pointer;
      animation: nanjiangPulse 2s ease-in-out infinite;
      transition: all 0.2s;
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  })
}

function addMarker(stn: StationInfo, L: any) {
  if (!mapInstance) return
  const icon = createMarkerIcon(stn, L)
  const marker = L.marker([stn.lat, stn.lng], { icon }).addTo(mapInstance)

  marker.bindPopup(`
    <div style="font-size:13px;line-height:1.8;min-width:170px;padding:2px 0">
      <b style="color:#52C41A">${stn.name}</b><br/>
      类型：${getTypeLabel(stn.type)}<br/>
      状态：<span style="color:${getStatusColor(stn.status)}">${getStatusLabel(stn.status)}</span><br/>
      经度：${stn.lng.toFixed(4)}°<br/>
      纬度：${stn.lat.toFixed(4)}°<br/>
      <span style="color:#52C41A;font-size:11px">📍 南江流域核心站</span>
    </div>
  `)

  marker.on('click', () => {
    emit('select', stn.id)
  })

  markers[stn.id] = marker
}

function removeMarker(stationId: string) {
  if (markers[stationId] && mapInstance) {
    mapInstance.removeLayer(markers[stationId])
    delete markers[stationId]
  }
}

function refreshAllMarkers(L: any) {
  // Remove all existing markers
  Object.keys(markers).forEach(id => removeMarker(id))
  // Re-add all
  localStations.value.forEach(stn => addMarker(stn, L))
}

let leafletRef: any = null

onMounted(async () => {
  const L = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  leafletRef = L
  if (!mapContainer.value) return

  // ── 初始化地图：聚焦南江流域 ──────────────────────────────
  mapInstance = L.map(mapContainer.value, {
    center: [29.05, 120.483],
    zoom: 10,
    zoomControl: false,
    attributionControl: false
  })

  // ── 天地图影像底图 + 注记 ──────────────────────────────────
  imgLayer = L.tileLayer(
    `https://t{s}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=${TIANDITU_KEY}`,
    { maxZoom: 18, subdomains: ['0','1','2','3','4','5','6','7'], attribution: '© 天地图' }
  )
  imgAnnLayer = L.tileLayer(
    `https://t{s}.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=${TIANDITU_KEY}`,
    { maxZoom: 18, subdomains: ['0','1','2','3','4','5','6','7'] }
  )

  // ── 天地图矢量底图 + 注记（备用）──────────────────────────
  vecLayer = L.tileLayer(
    `https://t{s}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=${TIANDITU_KEY}`,
    { maxZoom: 18, subdomains: ['0','1','2','3','4','5','6','7'], attribution: '© 天地图' }
  )
  vecAnnLayer = L.tileLayer(
    `https://t{s}.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=${TIANDITU_KEY}`,
    { maxZoom: 18, subdomains: ['0','1','2','3','4','5','6','7'] }
  )

  imgLayer.addTo(mapInstance)
  imgAnnLayer.addTo(mapInstance)

  // ── 绘制边界（浙江省 + 金华市 + 东阳市）────────────────────
  try {
    await initBoundaryLayers(L)
  } catch (error) {
    console.error('加载 GeoJSON 边界失败', error)
  }

  // ── 南江水库特殊标记 ──────────────────────────────────────
  L.marker([29.050, 120.483], {
    icon: L.divIcon({
      className: '',
      html: `<div style="
        width: 14px; height: 14px;
        background: linear-gradient(135deg, #52C41A, #00D4FF);
        border: 2px solid #fff;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        box-shadow: 0 0 10px rgba(82,196,26,0.8);
      "></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 14]
    })
  })
    .bindTooltip('南江水库<br>29°03′N 120°29′E', { direction: 'top', offset: [0, -16] })
    .addTo(mapInstance!)

  // ── 添加站点标记 ──────────────────────────────────────────
  localStations.value.forEach(stn => addMarker(stn, L))
})

// ── 选中站点时飞到该位置 ──────────────────────────────────────
watch(() => props.selectedId, (newId) => {
  const stn = localStations.value.find(s => s.id === newId)
  if (stn && mapInstance) {
    mapInstance.flyTo([stn.lat, stn.lng], 12, { duration: 0.9 })
    markers[newId]?.openPopup()
  }
})

// ── 站点管理 CRUD ─────────────────────────────────────────────

function openAddDialog() {
  isEdit.value = false
  dialogTitle.value = '新增站点'
  formError.value = ''
  Object.assign(stationForm, {
    id: '', name: '', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'water_level', lng: 120.483, lat: 29.050, status: 'online'
  })
  showStationDialog.value = true
}

function openEditDialog(stn: StationInfo) {
  isEdit.value = true
  dialogTitle.value = '编辑站点'
  formError.value = ''
  Object.assign(stationForm, { ...stn })
  showStationDialog.value = true
}

function validateForm(): boolean {
  if (!stationForm.name.trim()) { formError.value = '请输入站点名称'; return false }
  const lng = Number(stationForm.lng)
  const lat = Number(stationForm.lat)
  if (isNaN(lng) || lng < 118 || lng > 123) { formError.value = '经度应在 118°~123° 之间'; return false }
  if (isNaN(lat) || lat < 27 || lat > 32) { formError.value = '纬度应在 27°~32° 之间'; return false }
  formError.value = ''
  return true
}

function saveStation() {
  if (!validateForm()) return

  stationForm.lng = Number(stationForm.lng)
  stationForm.lat = Number(stationForm.lat)

  if (isEdit.value) {
    const idx = localStations.value.findIndex(s => s.id === stationForm.id)
    if (idx >= 0) {
      localStations.value[idx] = { ...stationForm }
      // 刷新地图标记
      removeMarker(stationForm.id)
      if (leafletRef) addMarker(localStations.value[idx], leafletRef)
    }
  } else {
    const newId = `stn-nj-${String(Date.now()).slice(-6)}`
    const newStn: StationInfo = { ...stationForm, id: newId }
    localStations.value.push(newStn)
    if (leafletRef) addMarker(newStn, leafletRef)
  }

  emit('stationsChange', [...localStations.value])
  showStationDialog.value = false
}

function deleteStation(stn: StationInfo) {
  if (!confirm(`确定删除站点「${stn.name}」？`)) return
  removeMarker(stn.id)
  localStations.value = localStations.value.filter(s => s.id !== stn.id)
  emit('stationsChange', [...localStations.value])
}

function locateStation(stn: StationInfo) {
  if (!mapInstance) return
  mapInstance.flyTo([stn.lat, stn.lng], 13, { duration: 0.8 })
  markers[stn.id]?.openPopup()
  emit('select', stn.id)
}

/** 切换行政边界显隐 */
function toggleBoundary() {
  showBoundary.value = !showBoundary.value
  if (!mapInstance || !boundaryLayer) return
  if (showBoundary.value) {
    boundaryLayer.addTo(mapInstance)
    showBoundaryLabels()
  } else {
    mapInstance.removeLayer(boundaryLayer)
    hideBoundaryLabels()
  }
}

/** 切换底图：影像 ↔ 矢量 */
function toggleBasemap() {
  if (!mapInstance) return
  if (basemapMode.value === 'img') {
    mapInstance.removeLayer(imgLayer)
    mapInstance.removeLayer(imgAnnLayer)
    vecLayer.addTo(mapInstance)
    vecAnnLayer.addTo(mapInstance)
    basemapMode.value = 'vec'
  } else {
    mapInstance.removeLayer(vecLayer)
    mapInstance.removeLayer(vecAnnLayer)
    imgLayer.addTo(mapInstance)
    imgAnnLayer.addTo(mapInstance)
    basemapMode.value = 'img'
  }
}

/** 定位到南江流域 */
function flyToNanjiang() {
  if (!mapInstance) return
  if (boundaryBounds?.isValid()) {
    mapInstance.flyToBounds(boundaryBounds, { padding: [30, 30], duration: 1.2 })
    return
  }
  mapInstance.flyTo([29.05, 120.483], 10, { duration: 1.2 })
}

defineExpose({ flyToNanjiang })
</script>

<template>
  <div class="map-panel card-panel">
    <div ref="mapContainer" class="map-container"></div>

    <!-- 工具栏 -->
    <div class="map-toolbar">
      <!-- 边界显隐 -->
      <button class="toolbar-btn" :class="{ active: showBoundary }" @click="toggleBoundary" title="省市边界">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3V6z"/>
          <path d="M9 3v15M15 6v15"/>
        </svg>
      </button>
      <!-- 底图切换 -->
      <button class="toolbar-btn" :class="{ active: basemapMode === 'vec' }" @click="toggleBasemap" :title="basemapMode === 'img' ? '切换矢量图' : '切换影像图'">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="9"/>
          <path d="M3 12h18M12 3c-2.5 4-2.5 14 0 18M12 3c2.5 4 2.5 14 0 18"/>
        </svg>
      </button>
      <!-- 站点管理 -->
      <button class="toolbar-btn" :class="{ active: showManagePanel }" @click="showManagePanel = !showManagePanel" title="站点管理">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>
          <line x1="19" y1="5" x2="5" y2="5"/><line x1="19" y1="12" x2="5" y2="12"/><line x1="19" y1="19" x2="5" y2="19"/>
        </svg>
      </button>
    </div>

    <!-- 站点管理面板 -->
    <div v-if="showManagePanel" class="manage-panel">
      <div class="manage-header">
        <span class="manage-title">站点管理</span>
        <div class="manage-actions">
          <button class="add-btn" @click="openAddDialog">+ 新增站点</button>
          <button class="close-panel-btn" @click="showManagePanel = false">✕</button>
        </div>
      </div>

      <div class="station-list">
        <div
          v-for="stn in localStations"
          :key="stn.id"
          class="station-row"
          :class="{ selected: stn.id === selectedId }"
        >
          <span class="status-dot" :style="{ background: getStatusColor(stn.status) }"></span>
          <div class="stn-info" @click="locateStation(stn)">
            <div class="stn-name">{{ stn.name }}</div>
            <div class="stn-meta">{{ getTypeLabel(stn.type) }} · {{ stn.lng.toFixed(3) }}°E {{ stn.lat.toFixed(3) }}°N</div>
          </div>
          <div class="stn-btns">
            <button class="icon-btn edit-btn" @click="openEditDialog(stn)" title="编辑">✏</button>
            <button class="icon-btn del-btn" @click="deleteStation(stn)" title="删除">🗑</button>
          </div>
        </div>

        <div v-if="localStations.length === 0" class="empty-tip">
          暂无站点，点击「新增站点」添加
        </div>
      </div>
    </div>

    <!-- 新增/编辑站点弹窗 -->
    <div v-if="showStationDialog" class="dialog-overlay" @click.self="showStationDialog = false">
      <div class="dialog-box">
        <div class="dialog-header">
          <span>{{ dialogTitle }}</span>
          <button class="close-btn" @click="showStationDialog = false">✕</button>
        </div>

        <div class="dialog-body">
          <div class="form-row">
            <label>站点名称 <em>*</em></label>
            <input v-model="stationForm.name" class="form-input" placeholder="如：南江支流站" />
          </div>

          <div class="form-row">
            <label>站点类型</label>
            <select v-model="stationForm.type" class="form-input">
              <option value="water_level">水位站</option>
              <option value="rainfall">雨量站</option>
              <option value="flow">流量站</option>
            </select>
          </div>

          <div class="form-row two-col">
            <div>
              <label>经度 <em>*</em></label>
              <input v-model.number="stationForm.lng" class="form-input" type="number" step="0.001" placeholder="120.483" />
            </div>
            <div>
              <label>纬度 <em>*</em></label>
              <input v-model.number="stationForm.lat" class="form-input" type="number" step="0.001" placeholder="29.050" />
            </div>
          </div>

          <div class="form-row">
            <label>状态</label>
            <select v-model="stationForm.status" class="form-input">
              <option value="online">正常</option>
              <option value="warning">预警</option>
              <option value="offline">离线</option>
            </select>
          </div>

          <div v-if="formError" class="form-error">⚠ {{ formError }}</div>
        </div>

        <div class="dialog-footer">
          <button class="btn-cancel" @click="showStationDialog = false">取消</button>
          <button class="btn-confirm" @click="saveStation">保存</button>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="map-legend">
      <span class="legend-item">
        <span class="dot" style="background:#1890FF"></span>正常
      </span>
      <span class="legend-item">
        <span class="dot" style="background:#FAAD14"></span>预警
      </span>
      <span class="legend-item">
        <span class="dot" style="background:#F5222D"></span>离线
      </span>
      <span class="legend-divider">|</span>
      <span class="legend-item">
        <span class="dot dot-province" style="background:#00D4FF"></span>浙江省
      </span>
      <span class="legend-item">
        <span class="dot dot-province" style="background:#FFD666"></span>金华市
      </span>
      <span class="legend-item">
        <span class="dot dot-basin" style="background:#52C41A"></span>东阳市
      </span>
    </div>

    <!-- 底图标签 -->
    <div class="basemap-tag">
      {{ basemapMode === 'img' ? '🛰 影像' : '🗺 矢量' }}
    </div>
  </div>
</template>

<style scoped>
.map-panel {
  flex: 1;
  position: relative;
  padding: 0;
  overflow: hidden;
}

.map-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

/* ── 工具栏 ── */
.map-toolbar {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 1000;
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(13, 27, 42, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.toolbar-btn:hover {
  background: rgba(13, 27, 42, 0.98);
  color: var(--text-primary);
  border-color: rgba(255,255,255,0.25);
}

.toolbar-btn.active {
  background: rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 212, 255, 0.6);
  color: #00D4FF;
}

/* ── 站点管理面板 ── */
.manage-panel {
  position: absolute;
  top: 10px;
  right: 52px;
  width: 300px;
  max-height: calc(100% - 80px);
  background: rgba(10, 20, 35, 0.95);
  border: 1px solid rgba(0, 212, 255, 0.25);
  border-radius: 8px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}

.manage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}

.manage-title {
  font-size: 13px;
  font-weight: 600;
  color: #00D4FF;
  letter-spacing: 0.5px;
}

.manage-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-btn {
  font-size: 12px;
  padding: 4px 10px;
  background: rgba(82, 196, 26, 0.2);
  border: 1px solid rgba(82, 196, 26, 0.5);
  border-radius: 4px;
  color: #52C41A;
  cursor: pointer;
  transition: all 0.2s;
}
.add-btn:hover {
  background: rgba(82, 196, 26, 0.35);
}

.close-panel-btn {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  transition: color 0.2s;
}
.close-panel-btn:hover { color: rgba(255,255,255,0.8); }

.station-list {
  overflow-y: auto;
  flex: 1;
  padding: 6px 0;
}

.station-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.station-row:hover {
  background: rgba(255,255,255,0.04);
}

.station-row.selected {
  background: rgba(0, 212, 255, 0.08);
  border-left: 2px solid #00D4FF;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.stn-info {
  flex: 1;
  min-width: 0;
}

.stn-name {
  font-size: 13px;
  color: var(--text-primary, #e6f0ff);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stn-meta {
  font-size: 11px;
  color: rgba(255,255,255,0.35);
  margin-top: 1px;
}

.stn-btns {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.icon-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px;
  color: rgba(255,255,255,0.45);
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
  color: #00D4FF;
}

.del-btn:hover {
  background: rgba(245, 34, 45, 0.15);
  border-color: rgba(245, 34, 45, 0.4);
  color: #F5222D;
}

.empty-tip {
  text-align: center;
  color: rgba(255,255,255,0.3);
  font-size: 12px;
  padding: 20px;
}

/* ── 弹窗 ── */
.dialog-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.55);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.dialog-box {
  background: #0d1b2a;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  width: 320px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  font-size: 14px;
  font-weight: 600;
  color: #00D4FF;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  font-size: 16px;
  transition: color 0.2s;
}
.close-btn:hover { color: rgba(255,255,255,0.8); }

.dialog-body {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-row.two-col {
  flex-direction: row;
  gap: 10px;
}
.form-row.two-col > div {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-row label {
  font-size: 12px;
  color: rgba(255,255,255,0.55);
}

.form-row label em {
  color: #F5222D;
  font-style: normal;
  margin-left: 2px;
}

.form-input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 5px;
  padding: 6px 10px;
  color: #e6f0ff;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: rgba(0, 212, 255, 0.5);
}

.form-input option {
  background: #0d1b2a;
}

.form-error {
  font-size: 12px;
  color: #F5222D;
  background: rgba(245, 34, 45, 0.1);
  border-radius: 4px;
  padding: 5px 10px;
}

.dialog-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.btn-cancel {
  padding: 6px 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 5px;
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.btn-cancel:hover {
  background: rgba(255,255,255,0.1);
}

.btn-confirm {
  padding: 6px 20px;
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.5);
  border-radius: 5px;
  color: #00D4FF;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-confirm:hover {
  background: rgba(0, 212, 255, 0.35);
}

/* ── 图例 ── */
.map-legend {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(13, 27, 42, 0.88);
  padding: 5px 12px;
  border-radius: 6px;
  z-index: 1000;
  font-size: 12px;
  color: var(--text-secondary);
  backdrop-filter: blur(4px);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-divider {
  color: rgba(255,255,255,0.15);
  font-size: 14px;
  margin: 0 2px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.dot-province {
  border-radius: 0;
  width: 12px;
  height: 2px;
  background: #00D4FF !important;
}

.dot-basin {
  box-shadow: 0 0 5px rgba(82,196,26,0.6);
}

.basemap-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(13, 27, 42, 0.82);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  z-index: 1000;
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(4px);
}

:global(.leaflet-container) {
  background: #0d1b2a;
}

:global(.leaflet-control-attribution) {
  background: rgba(13,27,42,0.7) !important;
  color: rgba(255,255,255,0.4) !important;
  font-size: 9px !important;
}
</style>

<style>
@keyframes nanjiangPulse {
  0%, 100% { box-shadow: 0 0 8px #1890FF; }
  50%       { box-shadow: 0 0 18px #1890FF, 0 0 32px rgba(24,144,255,0.4); }
}
</style>
