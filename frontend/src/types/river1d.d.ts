/**
 * River1D 一维河网建模 — 类型定义
 * M08 模块
 */

/** 坐标点（WGS84） */
export interface LatLng {
  lat: number
  lng: number
}

/** 河段（河道的一段折线） */
export interface Reach {
  id: string
  hydroId: string
  name: string
  coords: LatLng[]
}

/** 河道（可含多个河段） */
export interface River {
  id: string
  type: 'river'
  attrs: {
    hydroId: string
    name: string
    reachName: string
    length: number
    fromName: string
    toName: string
    notes: string
    [key: string]: unknown
  }
  reaches: Reach[]
}

/** 岸线（堤防） */
export interface Bank {
  id: string
  type: 'bank'
  coords: LatLng[]
  attrs: {
    name: string
    side: '左岸' | '右岸' | '无侧别'
    hydroId: string
    length: number
    notes: string
    [key: string]: unknown
  }
}

/** 横断面 */
export interface CrossSection {
  id: string
  type: 'section'
  coords: LatLng[]
  attrs: {
    hydroId: string
    name: string
    station: number
    reachId: string
    notes: string
    [key: string]: unknown
  }
}

/** 水工建筑物 */
export interface Structure {
  id: string
  type: 'structure'
  coords: LatLng[]
  attrs: {
    name: string
    stype: string
    station: number
    elev: number
    width: number
    hydroId: string
    notes: string
    [key: string]: unknown
  }
}

/** 拓扑节点 */
export interface TopoNode {
  id: string
  lat: number
  lng: number
  nodeType: 'upstream' | 'downstream' | 'junction'
  connectedRiverIds: string[]
}

/** 图层样式 */
export interface LayerStyle {
  color: string
  weight: number
  opacity: number
  dashArray: string
  showLabel: boolean
  labelField?: string
}

/** 节点样式 */
export interface NodeStyle {
  colorUpstream: string
  colorDownstream: string
  colorJunction: string
  radius: number
  showLabel: boolean
}

/** 项目信息 */
export interface ProjectInfo {
  name: string
  crs: string
  desc: string
}

/** 要素联合类型 */
export type AnyFeature = River | Bank | CrossSection | Structure

/** 绘制工具类型 */
export type DrawTool = 'select' | 'river' | 'bank' | 'section' | 'structure' | 'node'

/** 拓扑检查报告 */
export interface TopoReport {
  riverCount: number
  reachCount: number
  sectionCount: number
  nodeCount: number
  issues: string[]
  warnings: string[]
  ok: boolean
}

/** River1D 方案文件结构 (.r1d/.json) */
export interface River1dProjectFile {
  version: string
  savedAt: string
  project: ProjectInfo
  rivers: River[]
  banks: Bank[]
  sections: CrossSection[]
  structures: Structure[]
  nodes: TopoNode[]
}
