/** 用户信息 */
export interface UserInfo {
  id: string
  username: string
  name: string
  role: UserRole
  department: string
  phone: string
  email: string
  lastLogin: string
}

/** 用户角色 */
export type UserRole = 'admin' | 'province' | 'city' | 'county' | 'viewer'

/** 角色显示名称 */
export const RoleLabels: Record<UserRole, string> = {
  admin: '超级管理员',
  province: '省级用户',
  city: '市级用户',
  county: '县级用户',
  viewer: '观察员'
}

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** 登录响应 */
export interface LoginResponse {
  token: string
  user: UserInfo
}

/** 帕累托优化方案 */
export interface ParetoSolution {
  id: string
  floodBenefit: number       // 防洪效益 (0-1)
  powerBenefit: number       // 发电效益 (0-1)
  waterSupplyBenefit: number // 供水效益 (0-1)
  ecoBenefit: number         // 生态效益 (0-1)
  isRecommended: boolean
  schedule: SchedulePoint[]
}

/** 调度时间点 */
export interface SchedulePoint {
  time: string
  gateOpening: number   // 闸门开度 (%)
  discharge: number     // 泄流量 (m³/s)
}

/** 系统日志 */
export interface SystemLog {
  id: string
  timestamp: string
  userId: string
  userName: string
  action: string
  module: string
  detail: string
  ip: string
}
