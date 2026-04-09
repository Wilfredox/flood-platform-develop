<script setup lang="ts">
/**
 * River1DPage.vue — River1D 建模工作台页面骨架 (R1)
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import R1DToolbar from './components/R1DToolbar.vue'
import R1DMap from './components/R1DMap.vue'
import R1DRightPanel from './components/R1DRightPanel.vue'
import { useRiver1dStore } from '@/stores/useRiver1dStore'
import type { River1dProjectFile } from '@/types/river1d'

const router = useRouter()
const store = useRiver1dStore()
const r1dMapRef = ref<InstanceType<typeof R1DMap> | null>(null)
const reportVisible = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  // 恢复状态或清除
  store.resetProject()
})

// === Toolbar Events ===
function handleFitAll() {
  r1dMapRef.value?.fitAll()
}

function handleFlyTo(coords: Array<{ lat: number; lng: number }>) {
  r1dMapRef.value?.flyToCoords(coords)
}

function handleCancelDraw() {
  r1dMapRef.value?.cancelCurrentDraw()
  store.setTool('select')
}

function handleGenNodes(showReport = true) {
  const cnt = store.autoGenNodes()
  r1dMapRef.value?.renderNodes()
  if (showReport) {
    ElMessage.success(`成功生成 ${cnt} 个节点`)
  }
}

function handleCheckTopo() {
  store.checkTopo()
  reportVisible.value = true
}

function handleNewProject() {
  ElMessageBox.confirm('新建方案将清除当前所有未保存数据，是否继续？', '新建方案', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    store.resetProject()
    ElMessage.success('已新建方案')
  }).catch(() => {})
}

function handleOpenProject() {
  fileInputRef.value?.click()
}

function handleSaveProject() {
  // 快速保存：使用当前项目名导出为 .r1d
  downloadProjectFile(`${store.project.name || 'river1d-project'}.r1d`)
  store.isDirty = false
  ElMessage.success('方案保存成功')
}

function handleSaveProjectAs() {
  ElMessageBox.prompt('请输入另存为文件名（无需扩展名）', '另存为方案', {
    inputValue: store.project.name || 'river1d-project',
    confirmButtonText: '保存',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    const name = (value || '').trim() || 'river1d-project'
    store.setProjectName(name)
    downloadProjectFile(`${name}.r1d`)
    store.isDirty = false
    ElMessage.success('方案另存为成功')
  }).catch(() => {})
}

function handleExportData() {
  const data = store.toProjectFile()
  const featureCollection = {
    type: 'FeatureCollection',
    features: [
      ...store.rivers.flatMap(r => r.reaches.map(rc => ({
        type: 'Feature',
        properties: { id: r.id, type: 'river', ...r.attrs, reachId: rc.id, reachName: rc.name },
        geometry: { type: 'LineString', coordinates: rc.coords.map(p => [p.lng, p.lat]) }
      }))),
      ...store.banks.map(b => ({
        type: 'Feature',
        properties: { id: b.id, type: 'bank', ...b.attrs },
        geometry: { type: 'LineString', coordinates: b.coords.map(p => [p.lng, p.lat]) }
      })),
      ...store.sections.map(s => ({
        type: 'Feature',
        properties: { id: s.id, type: 'section', ...s.attrs },
        geometry: { type: 'LineString', coordinates: s.coords.map(p => [p.lng, p.lat]) }
      })),
      ...store.structures.map(s => ({
        type: 'Feature',
        properties: { id: s.id, type: 'structure', ...s.attrs },
        geometry: { type: 'LineString', coordinates: s.coords.map(p => [p.lng, p.lat]) }
      }))
    ]
  }

  downloadBlob(`${store.project.name || 'river1d-project'}.geojson`, JSON.stringify(featureCollection, null, 2), 'application/geo+json')
  downloadBlob(`${store.project.name || 'river1d-project'}.json`, JSON.stringify(data, null, 2), 'application/json')
  ElMessage.success('已导出 GeoJSON + JSON')
}

function handleProjectFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    try {
      const text = String(reader.result || '')
      const payload = JSON.parse(text) as River1dProjectFile
      store.loadProjectFile(payload)
      ElMessage.success(`方案打开成功：${store.project.name}`)
      handleFitAll()
    } catch {
      ElMessage.error('方案文件解析失败，请检查文件格式')
    } finally {
      input.value = ''
    }
  }
  reader.readAsText(file)
}

function downloadProjectFile(fileName: string) {
  const payload = store.toProjectFile()
  downloadBlob(fileName, JSON.stringify(payload, null, 2), 'application/json')
}

function downloadBlob(fileName: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fileName
  a.click()
  URL.revokeObjectURL(url)
}

function goBack() {
  router.push('/dashboard')
}

function goMuskingum() {
  router.push('/river1d/muskingum')
}
</script>

<template>
  <div class="river1d-page">
    <!-- Header -->
    <header class="r1d-header">
      <div class="hd-brand" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; cursor: pointer;">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        <div class="hd-logo">
          <svg viewBox="0 0 15 15">
            <path d="M2 11C4 8 6 6 7.5 8C9 10 11 7 13 5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <div class="hd-name">River1D</div>
          <div class="hd-ver">v7.0 · {{ store.project.crs }}</div>
        </div>
      </div>
      <div class="hd-project-name">
        {{ store.project.name }} <span v-if="store.isDirty" style="color: #f4a261">*</span>
      </div>
      <button class="hd-muskingum-btn" @click="goMuskingum">分段马斯金根</button>
    </header>

    <input
      ref="fileInputRef"
      type="file"
      accept=".r1d,.json"
      style="display: none"
      @change="handleProjectFileChange"
    >

    <!-- Toolbar -->
    <R1DToolbar
      @fitAll="handleFitAll"
      @cancelDraw="handleCancelDraw"
      @genNodes="handleGenNodes"
      @checkTopo="handleCheckTopo"
      @newProject="handleNewProject"
      @openProject="handleOpenProject"
      @saveProject="handleSaveProject"
      @saveProjectAs="handleSaveProjectAs"
      @exportData="handleExportData"
    />

    <!-- Main Workspace -->
    <div class="r1d-workspace">
      <!-- 左侧导航 (简化版) -->
      <nav class="r1d-sidebar">
        <button class="sb-btn active" title="图层管理">
          <svg viewBox="0 0 18 18"><rect x="2" y="2" width="14" height="3.5" rx="1"/><rect x="2" y="7.5" width="14" height="3.5" rx="1"/><rect x="2" y="13" width="14" height="3.5" rx="1"/></svg>
        </button>
      </nav>

      <!-- 地图 -->
      <R1DMap ref="r1dMapRef" />

      <!-- 右侧面板 -->
      <R1DRightPanel
        @genNodes="handleGenNodes"
        @checkTopo="handleCheckTopo"
        @flyTo="handleFlyTo"
      />
    </div>

    <!-- 拓扑检查报告弹窗 -->
    <el-dialog v-model="reportVisible" title="拓扑检查报告" width="500px">
      <div v-if="store.topoReport">
        <div style="margin-bottom: 12px; font-weight: 600;">
          概览：河道 {{ store.topoReport.riverCount }} | 段 {{ store.topoReport.reachCount }} | 断面 {{ store.topoReport.sectionCount }} | 节点 {{ store.topoReport.nodeCount }}
        </div>

        <el-alert v-if="store.topoReport.ok" type="success" title="拓扑结构正常，未发现错误。" :closable="false" show-icon />

        <div v-if="store.topoReport.issues.length > 0" style="margin-top: 16px;">
          <h4 style="color: #F56C6C; margin-bottom: 8px;">错误 ({{ store.topoReport.issues.length }})</h4>
          <ul style="padding-left: 20px; color: #606266; font-size: 13px;">
            <li v-for="(iss, i) in store.topoReport.issues" :key="i" style="margin-bottom: 4px;">{{ iss }}</li>
          </ul>
        </div>

        <div v-if="store.topoReport.warnings.length > 0" style="margin-top: 16px;">
          <h4 style="color: #E6A23C; margin-bottom: 8px;">警告 ({{ store.topoReport.warnings.length }})</h4>
          <ul style="padding-left: 20px; color: #606266; font-size: 13px;">
            <li v-for="(war, i) in store.topoReport.warnings" :key="i" style="margin-bottom: 4px;">{{ war }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="reportVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.river1d-page {
  font-family: 'DM Sans', 'HarmonyOS Sans', sans-serif;
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* Header */
.r1d-header {
  height: 48px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 16px;
  flex-shrink: 0;
  z-index: 400;
}

.hd-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #fff;
}

.hd-logo {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: linear-gradient(140deg, #00b4d8, #1a6cff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.hd-name {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -.3px;
  line-height: 1;
}

.hd-ver {
  color: rgba(255,255,255,.3);
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 3px;
  line-height: 1;
}

.hd-project-name {
  margin-left: max(20px, auto);
  margin-right: max(20px, auto);
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255,255,255,.8);
  font-size: 13px;
  font-weight: 500;
}

.hd-muskingum-btn {
  margin-left: auto;
  height: 30px;
  padding: 0 12px;
  border: 1px solid #2b5f7d;
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.18);
  color: #d7ffe6;
  font-size: 12px;
  cursor: pointer;
}

.hd-muskingum-btn:hover {
  background: rgba(34, 197, 94, 0.3);
}

/* Workspace */
.r1d-workspace {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.r1d-sidebar {
  width: 48px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  z-index: 200;
  flex-shrink: 0;
}

.sb-btn {
  width: 36px;
  height: 36px;
  border-radius: 7px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--text-secondary);
  transition: all .15s;
}

.sb-btn svg {
  width: 17px;
  height: 17px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sb-btn.active {
  background: rgba(24,144,255,.16);
  color: var(--color-primary);
}
</style>
