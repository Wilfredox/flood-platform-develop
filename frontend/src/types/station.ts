/** 站点信息 */
export interface StationInfo {
  id: string
  name: string
  basinId: string
  basinName: string
  type: 'water_level' | 'rainfall' | 'flow'
  lng: number
  lat: number
  status: 'online' | 'offline' | 'warning'
}

/** 流域-站点树结构 */
export interface BasinTree {
  id: string
  label: string
  children: { id: string; label: string; status: string }[]
}

/** 传感器实时数据 */
export interface SensorReading {
  stationId: string
  stationName: string
  timestamp: string
  waterLevel: number      // 米
  rainfall: number        // mm/h
  flow: number            // m³/s
  alertLevel: AlertLevel
}

/** 预警等级 */
export type AlertLevel = 'BLUE' | 'YELLOW' | 'ORANGE' | 'RED' | 'NORMAL'

/** 预警事件 */
export interface AlertEvent {
  id: string
  stationId: string
  stationName: string
  level: AlertLevel
  metric: string
  value: number
  threshold: number
  timestamp: string
  message: string
}

/** 预警规则 */
export interface AlertRule {
  id: string
  stationId: string
  stationName: string
  metric: 'waterLevel' | 'rainfall' | 'flow'
  blueThreshold: number
  yellowThreshold: number
  orangeThreshold: number
  redThreshold: number
  enabled: boolean
}
