/**
 * 南江流域水文站点 Mock 数据
 * 主页仅展示南江流域站点
 * 生产版本将从 data-ingest-service 获取真实传感器数据
 */
import type { StationInfo, BasinTree, SensorReading, AlertEvent, AlertLevel } from '@/types/station'

/** 流域-站点树数据（仅南江流域） */
export const mockBasinTree: BasinTree[] = [
  {
    id: 'basin-nanjiang',
    label: '南江流域',
    children: [
      { id: 'stn-nj-001', label: '南江水库站', status: 'online' },
      { id: 'stn-nj-002', label: '南江坝下站', status: 'warning' },
      { id: 'stn-nj-003', label: '南江干流站', status: 'online' },
      { id: 'stn-nj-004', label: '东溪支流站', status: 'online' },
      { id: 'stn-nj-005', label: '西溪支流站', status: 'offline' }
    ]
  }
]

/** Mock 站点详细信息（仅南江流域，坐标均在浙江省内） */
export const mockStations: StationInfo[] = [
  // ── 南江流域（核心展示区，南江水库 29.05°N, 120.483°E 为中心）──
  { id: 'stn-nj-001', name: '南江水库站', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'water_level', lng: 120.483, lat: 29.050, status: 'online' },
  { id: 'stn-nj-002', name: '南江坝下站', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'flow',        lng: 120.495, lat: 29.038, status: 'warning' },
  { id: 'stn-nj-003', name: '南江干流站', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'water_level', lng: 120.420, lat: 28.985, status: 'online' },
  { id: 'stn-nj-004', name: '东溪支流站', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'rainfall',    lng: 120.560, lat: 29.120, status: 'online' },
  { id: 'stn-nj-005', name: '西溪支流站', basinId: 'basin-nanjiang', basinName: '南江流域',
    type: 'rainfall',    lng: 120.380, lat: 29.080, status: 'offline' }
]

/** 生成 Mock 实时读数 */
export function generateMockReading(stationId: string): SensorReading {
  const station = mockStations.find(s => s.id === stationId)
  const waterLevel = +(184 + Math.random() * 6).toFixed(2)
  const rainfall = +(Math.random() * 30).toFixed(1)
  const flow = +(Math.random() * 5000 + 500).toFixed(0)
  const alertLevel = evaluateAlertNanjiang(waterLevel)

  return {
    stationId,
    stationName: station?.name || '未知站点',
    timestamp: new Date().toISOString(),
    waterLevel,
    rainfall,
    flow,
    alertLevel
  }
}

/** 生成 24 小时历史数据 */
export function generateHistory24h(stationId: string): SensorReading[] {
  const data: SensorReading[] = []
  const station = mockStations.find(s => s.id === stationId)
  const now = Date.now()
  const baseLevel = 185 + Math.random() * 2

  for (let i = 24; i >= 0; i--) {
    const t = now - i * 3600 * 1000
    const peak = Math.exp(-((i - 12) ** 2) / 50) * 4
    const waterLevel = +(baseLevel + peak + (Math.random() - 0.5) * 0.5).toFixed(2)
    const rainfall = +(Math.max(0, 10 - i * 0.3 + Math.random() * 8)).toFixed(1)
    const flow = +(waterLevel * 15 + Math.random() * 300).toFixed(0)

    data.push({
      stationId,
      stationName: station?.name || '未知站点',
      timestamp: new Date(t).toISOString(),
      waterLevel,
      rainfall,
      flow,
      alertLevel: evaluateAlertNanjiang(waterLevel)
    })
  }
  return data
}

/** 南江水库水位预警等级（汛限水位 188m） */
function evaluateAlertNanjiang(waterLevel: number): AlertLevel {
  if (waterLevel >= 191.0) return 'RED'
  if (waterLevel >= 189.5) return 'ORANGE'
  if (waterLevel >= 188.0) return 'YELLOW'
  if (waterLevel >= 186.5) return 'BLUE'
  return 'NORMAL'
}

/** Mock 预警事件 */
export const mockAlerts: AlertEvent[] = [
  {
    id: 'alert-001', stationId: 'stn-nj-002', stationName: '南江坝下站',
    level: 'ORANGE', metric: '流量', value: 3850, threshold: 3200,
    timestamp: new Date(Date.now() - 300000).toISOString(),
    message: '南江坝下流量超警戒值，建议关注下游防洪态势'
  },
  {
    id: 'alert-002', stationId: 'stn-nj-001', stationName: '南江水库站',
    level: 'YELLOW', metric: '水位', value: 188.6, threshold: 188.0,
    timestamp: new Date(Date.now() - 600000).toISOString(),
    message: '南江水库水位超汛限水位，持续关注上涨趋势'
  },
  {
    id: 'alert-003', stationId: 'stn-nj-004', stationName: '东溪支流站',
    level: 'BLUE', metric: '降雨量', value: 28.5, threshold: 25.0,
    timestamp: new Date(Date.now() - 1500000).toISOString(),
    message: '南江东溪支流降雨偏强，关注汇流影响'
  }
]
