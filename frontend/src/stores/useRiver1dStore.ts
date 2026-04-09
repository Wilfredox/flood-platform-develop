/**
 * River1D Pinia Store — M08 一维河网建模状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  River, Bank, CrossSection, Structure, TopoNode,
  DrawTool, ProjectInfo, TopoReport, LatLng, LayerStyle, NodeStyle, River1dProjectFile
} from '@/types/river1d'

// HydroID 计数器
const hydroCnt: Record<string, number> = { river: 0, reach: 0, bank: 0, section: 0, structure: 0 }
function nextHydroId(type: string): string {
  hydroCnt[type] = (hydroCnt[type] || 0) + 1
  return `${type.toUpperCase()}-${String(hydroCnt[type]).padStart(3, '0')}`
}

export const useRiver1dStore = defineStore('river1d', () => {
  // ── 工具状态 ──────────────────────────────────────────
  const activeTool = ref<DrawTool>('select')
  const snapEnabled = ref(true)

  // ── 方案信息 ──────────────────────────────────────────
  const project = ref<ProjectInfo>({
    name: '新方案',
    crs: 'CGCS2000_3TM_120',
    desc: ''
  })
  const isDirty = ref(false)

  // ── 要素数据 ──────────────────────────────────────────
  const rivers = ref<River[]>([])
  const banks = ref<Bank[]>([])
  const sections = ref<CrossSection[]>([])
  const structures = ref<Structure[]>([])
  const nodes = ref<TopoNode[]>([])

  // ── 选中状态 ──────────────────────────────────────────
  const selectedFeature = ref<River | Bank | CrossSection | Structure | null>(null)

  // ── 图层样式 ──────────────────────────────────────────
  const layerStyles = ref<Record<string, LayerStyle>>({
    river:     { color: '#1a6cff', weight: 3,   opacity: 0.9, dashArray: '',      showLabel: false, labelField: 'name' },
    bank:      { color: '#00a878', weight: 2.5, opacity: 0.9, dashArray: '10 5', showLabel: false, labelField: 'name' },
    section:   { color: '#f4a261', weight: 2.5, opacity: 1.0, dashArray: '10 4', showLabel: true,  labelField: 'name' },
    structure: { color: '#e63946', weight: 3.5, opacity: 1.0, dashArray: '',      showLabel: true,  labelField: 'name' },
  })
  const nodeStyle = ref<NodeStyle>({
    colorUpstream: '#00a878',
    colorDownstream: '#e63946',
    colorJunction: '#6c63ff',
    radius: 6,
    showLabel: true
  })

  // ── 图层可见性 ────────────────────────────────────────
  const layerVisible = ref<Record<string, boolean>>({
    river: true, bank: true, section: true, structure: true, nodes: true
  })

  // ── 撤销栈 ────────────────────────────────────────────
  const undoStack = ref<Array<{ type: string; action: string; data: unknown }>>([])

  // ── 拓扑结果 ──────────────────────────────────────────
  const topoReport = ref<TopoReport | null>(null)
  const topoTolerance = ref(1.0) // 捕捉容差 (m)

  // ── 统计 ──────────────────────────────────────────────
  const stats = computed(() => ({
    riverCount: rivers.value.length,
    reachCount: rivers.value.reduce((s, r) => s + r.reaches.length, 0),
    sectionCount: sections.value.length,
    structureCount: structures.value.length,
    bankCount: banks.value.length,
    nodeCount: nodes.value.length,
  }))

  // ── 操作：设置工具 ────────────────────────────────────
  function setTool(tool: DrawTool) {
    activeTool.value = tool
  }

  function toggleSnap() {
    snapEnabled.value = !snapEnabled.value
  }

  // ── 操作：新建 River（从绘制完成的坐标） ──────────────
  function addRiver(coords: LatLng[]): River {
    const riverHydroId = nextHydroId('river')
    const reachHydroId = nextHydroId('reach')
    const river: River = {
      id: `river_${Date.now()}`,
      type: 'river',
      attrs: {
        hydroId: riverHydroId,
        name: `河道-${String(rivers.value.length + 1).padStart(2, '0')}`,
        reachName: `河段-${String(1).padStart(2, '0')}`,
        length: calcLength(coords),
        fromName: '--',
        toName: '--',
        notes: ''
      },
      reaches: [{
        id: `reach_${Date.now()}`,
        hydroId: reachHydroId,
        name: `Reach-${reachHydroId}`,
        coords: [...coords]
      }]
    }
    rivers.value.push(river)
    undoStack.value.push({ type: 'river', action: 'add', data: river.id })
    isDirty.value = true
    return river
  }

  function addBank(coords: LatLng[]): Bank {
    const bank: Bank = {
      id: `bank_${Date.now()}`,
      type: 'bank',
      coords: [...coords],
      attrs: {
        name: `岸线-${String(banks.value.length + 1).padStart(2, '0')}`,
        side: '左岸',
        hydroId: '',
        length: calcLength(coords),
        notes: ''
      }
    }
    banks.value.push(bank)
    undoStack.value.push({ type: 'bank', action: 'add', data: bank.id })
    isDirty.value = true
    return bank
  }

  function addSection(coords: LatLng[]): CrossSection {
    const sec: CrossSection = {
      id: `section_${Date.now()}`,
      type: 'section',
      coords: [...coords],
      attrs: {
        hydroId: nextHydroId('section'),
        name: `CS-${String(sections.value.length + 1).padStart(3, '0')}`,
        station: 0,
        reachId: '',
        notes: ''
      }
    }
    sections.value.push(sec)
    undoStack.value.push({ type: 'section', action: 'add', data: sec.id })
    isDirty.value = true
    return sec
  }

  function addStructure(coords: LatLng[]): Structure {
    const st: Structure = {
      id: `structure_${Date.now()}`,
      type: 'structure',
      coords: [...coords],
      attrs: {
        name: `建筑物-${String(structures.value.length + 1).padStart(2, '0')}`,
        stype: '水闸',
        station: 0,
        elev: 0,
        width: 0,
        hydroId: '',
        notes: ''
      }
    }
    structures.value.push(st)
    undoStack.value.push({ type: 'structure', action: 'add', data: st.id })
    isDirty.value = true
    return st
  }

  // ── 撤销 ──────────────────────────────────────────────
  function undoLast() {
    const last = undoStack.value.pop()
    if (!last) return
    if (last.type === 'river')     rivers.value     = rivers.value.filter(r => r.id !== last.data)
    if (last.type === 'bank')      banks.value      = banks.value.filter(b => b.id !== last.data)
    if (last.type === 'section')   sections.value   = sections.value.filter(s => s.id !== last.data)
    if (last.type === 'structure') structures.value = structures.value.filter(s => s.id !== last.data)
    isDirty.value = true
  }

  // ── 清空图层 ──────────────────────────────────────────
  function clearLayer(type: string) {
    if (type === 'river')     rivers.value     = []
    if (type === 'bank')      banks.value      = []
    if (type === 'section')   sections.value   = []
    if (type === 'structure') structures.value = []
    if (type === 'nodes')     nodes.value      = []
    if (selectedFeature.value && selectedFeature.value.type === type) {
      selectedFeature.value = null
    }
    isDirty.value = true
  }

  // ── 属性编辑（R6） ──────────────────────────────────
  function updateSelectedAttrs(patch: Record<string, unknown>) {
    const selected = selectedFeature.value
    if (!selected) return

    selected.attrs = {
      ...selected.attrs,
      ...patch
    }
    isDirty.value = true
  }

  // ── 项目元信息编辑（R8） ─────────────────────────────
  function setProjectName(name: string) {
    const trimmed = name.trim()
    if (!trimmed) return
    project.value.name = trimmed
    isDirty.value = true
  }

  // ── 方案序列化/反序列化（R8） ────────────────────────
  function toProjectFile(): River1dProjectFile {
    return {
      version: '1.0.0',
      savedAt: new Date().toISOString(),
      project: { ...project.value },
      rivers: JSON.parse(JSON.stringify(rivers.value)),
      banks: JSON.parse(JSON.stringify(banks.value)),
      sections: JSON.parse(JSON.stringify(sections.value)),
      structures: JSON.parse(JSON.stringify(structures.value)),
      nodes: JSON.parse(JSON.stringify(nodes.value))
    }
  }

  function loadProjectFile(payload: River1dProjectFile) {
    if (!payload || !payload.project) {
      throw new Error('方案文件缺少 project 字段')
    }

    project.value = {
      name: payload.project.name || '未命名方案',
      crs: payload.project.crs || 'CGCS2000_3TM_120',
      desc: payload.project.desc || ''
    }
    rivers.value = Array.isArray(payload.rivers) ? payload.rivers : []
    banks.value = Array.isArray(payload.banks) ? payload.banks : []
    sections.value = Array.isArray(payload.sections) ? payload.sections : []
    structures.value = Array.isArray(payload.structures) ? payload.structures : []
    nodes.value = Array.isArray(payload.nodes) ? payload.nodes : []

    selectedFeature.value = null
    topoReport.value = null
    undoStack.value = []
    isDirty.value = false
  }

  // ── 自动生成拓扑节点 (R5) ─────────────────────────────
  function autoGenNodes() {
    const tolDeg = topoTolerance.value / 111320 // m → 近似度
    const newNodes: TopoNode[] = []
    let nodeIdx = 1

    type EndPoint = { lat: number; lng: number; nodeType: 'upstream' | 'downstream'; riverId: string }
    const endpoints: EndPoint[] = []

    rivers.value.forEach(river => {
      if (!river.reaches.length) return
      const firstReach = river.reaches[0]
      const lastReach  = river.reaches[river.reaches.length - 1]
      const start = firstReach.coords[0]
      const end   = lastReach.coords[lastReach.coords.length - 1]
      if (start) endpoints.push({ lat: start.lat, lng: start.lng, nodeType: 'upstream',   riverId: river.id })
      if (end)   endpoints.push({ lat: end.lat,   lng: end.lng,   nodeType: 'downstream', riverId: river.id })
    })

    // 聚合距离容差内的端点为同一节点
    const visited = new Set<number>()
    endpoints.forEach((ep, i) => {
      if (visited.has(i)) return
      const connected: string[] = [ep.riverId]
      const nearby: number[] = [i]
      endpoints.forEach((other, j) => {
        if (i === j) return
        const d = Math.hypot(ep.lat - other.lat, ep.lng - other.lng)
        if (d < tolDeg) { nearby.push(j); visited.add(j); connected.push(other.riverId) }
      })
      visited.add(i)
      const isJunction = connected.length > 2
      newNodes.push({
        id: `N${String(nodeIdx++).padStart(3, '0')}`,
        lat: ep.lat,
        lng: ep.lng,
        nodeType: isJunction ? 'junction' : ep.nodeType,
        connectedRiverIds: [...new Set(connected)]
      })
    })

    nodes.value = newNodes
    isDirty.value = true
    return newNodes.length
  }

  // ── 拓扑检查 (R5) ─────────────────────────────────────
  function checkTopo(): TopoReport {
    const issues: string[] = []
    const warnings: string[] = []

    if (rivers.value.length === 0) issues.push('未绘制任何河道，无法进行拓扑检查')

    rivers.value.forEach(r => {
      if (!r.reaches.length) issues.push(`河道「${r.attrs.name}」无河段数据`)
      r.reaches.forEach(rc => {
        if (rc.coords.length < 2) issues.push(`河段「${rc.name}」坐标点不足（至少需要2个点）`)
      })
    })

    // 断面检测：断面应与河道相交
    if (sections.value.length > 0 && rivers.value.length === 0) {
      warnings.push('存在横断面但无河道，断面里程无法计算')
    }

    const report: TopoReport = {
      riverCount: rivers.value.length,
      reachCount: rivers.value.reduce((s, r) => s + r.reaches.length, 0),
      sectionCount: sections.value.length,
      nodeCount: nodes.value.length,
      issues,
      warnings,
      ok: issues.length === 0
    }
    topoReport.value = report
    return report
  }

  // ── 重置项目 ──────────────────────────────────────────
  function resetProject(info: Partial<ProjectInfo> = {}) {
    rivers.value     = []
    banks.value      = []
    sections.value   = []
    structures.value = []
    nodes.value      = []
    undoStack.value  = []
    selectedFeature.value = null
    topoReport.value = null
    Object.keys(hydroCnt).forEach(k => hydroCnt[k] = 0)
    project.value = { name: info.name ?? '新方案', crs: info.crs ?? 'CGCS2000_3TM_120', desc: info.desc ?? '' }
    isDirty.value = false
  }

  // ── 选中要素 ──────────────────────────────────────────
  function selectFeature(f: River | Bank | CrossSection | Structure | null) {
    selectedFeature.value = f
  }

  // ── 计算折线长度（米，使用 Haversine） ────────────────
  function calcLength(coords: LatLng[]): number {
    let total = 0
    for (let i = 1; i < coords.length; i++) {
      const a = coords[i - 1], b = coords[i]
      const R = 6371000
      const φ1 = a.lat * Math.PI / 180, φ2 = b.lat * Math.PI / 180
      const Δφ = (b.lat - a.lat) * Math.PI / 180
      const Δλ = (b.lng - a.lng) * Math.PI / 180
      const x = Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2
      total += 2 * R * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x))
    }
    return Math.round(total)
  }

  return {
    // state
    activeTool, snapEnabled, project, isDirty,
    rivers, banks, sections, structures, nodes,
    selectedFeature, layerStyles, nodeStyle, layerVisible,
    undoStack, topoReport, topoTolerance, stats,
    // actions
    setTool, toggleSnap,
    addRiver, addBank, addSection, addStructure,
    undoLast, clearLayer,
    autoGenNodes, checkTopo,
    resetProject, selectFeature,
    updateSelectedAttrs, setProjectName,
    toProjectFile, loadProjectFile
  }
})
