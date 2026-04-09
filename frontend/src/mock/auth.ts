/**
 * [DEMO-ONLY] Mock 用户与认证数据
 * 生产版本将从 auth-service JWT 验证
 */
import type { UserInfo, UserRole, LoginResponse } from '@/types/common'

/** 内置测试账号 */
const mockUsers: Record<string, { password: string; user: UserInfo }> = {
  admin: {
    password: 'admin123',
    user: {
      id: 'u-001', username: 'admin', name: '系统管理员',
      role: 'admin', department: '信息中心',
      phone: '13800000001', email: 'admin@flood.gov.cn',
      lastLogin: '2026-03-06 18:30:00'
    }
  },
  province: {
    password: 'p123',
    user: {
      id: 'u-002', username: 'province', name: '张省长',
      role: 'province', department: '省水利厅',
      phone: '13800000002', email: 'province@flood.gov.cn',
      lastLogin: '2026-03-06 15:20:00'
    }
  },
  city: {
    password: 'c123',
    user: {
      id: 'u-003', username: 'city', name: '李市长',
      role: 'city', department: '市水务局',
      phone: '13800000003', email: 'city@flood.gov.cn',
      lastLogin: '2026-03-05 09:00:00'
    }
  },
  county: {
    password: 'co123',
    user: {
      id: 'u-004', username: 'county', name: '王县长',
      role: 'county', department: '县水利局',
      phone: '13800000004', email: 'county@flood.gov.cn',
      lastLogin: '2026-03-06 10:15:00'
    }
  },
  viewer: {
    password: 'v123',
    user: {
      id: 'u-005', username: 'viewer', name: '观察员甲',
      role: 'viewer', department: '社会公众',
      phone: '13800000005', email: 'viewer@flood.gov.cn',
      lastLogin: '2026-03-04 20:00:00'
    }
  }
}

/** Mock 登录验证 */
export function mockLogin(username: string, password: string): LoginResponse | null {
  const entry = mockUsers[username]
  if (entry && entry.password === password) {
    // [DEMO-ONLY] 生成伪 JWT token
    const fakeToken = btoa(JSON.stringify({
      sub: entry.user.id,
      username: entry.user.username,
      role: entry.user.role,
      exp: Date.now() + 3600000 * 24
    }))
    return {
      token: `demo.${fakeToken}.mock`,
      user: { ...entry.user, lastLogin: new Date().toLocaleString('zh-CN') }
    }
  }
  return null
}

/** 获取所有用户（管理页面用） */
export function getMockUsers(): UserInfo[] {
  return Object.values(mockUsers).map(e => e.user)
}

/** 角色可访问的菜单 */
export const roleMenus: Record<UserRole, string[]> = {
  admin: ['dashboard', 'detail', 'admin-stations', 'admin-alerts', 'admin-users', 'admin-logs'],
  province: ['dashboard', 'detail', 'admin-stations', 'admin-alerts', 'admin-logs'],
  city: ['dashboard', 'detail', 'admin-stations'],
  county: ['dashboard', 'detail'],
  viewer: ['dashboard']
}
