/**
 * [DEMO-ONLY] Mock 系统日志数据
 */
import type { SystemLog } from '@/types/common'

const actions = ['登录系统', '查看大屏', '修改预警规则', '导出数据', '新增站点', '删除用户', '启动优化计算', '查看日志']
const modules = ['认证模块', '数据大屏', '预警引擎', '数据导出', '站点管理', '用户管理', '优化服务', '系统日志']
const users = ['系统管理员', '张省长', '李市长', '王县长', '观察员甲']

export function generateMockLogs(count: number = 50): SystemLog[] {
  const logs: SystemLog[] = []
  for (let i = 0; i < count; i++) {
    const idx = Math.floor(Math.random() * actions.length)
    logs.push({
      id: `log-${String(i + 1).padStart(4, '0')}`,
      timestamp: new Date(Date.now() - i * 600000 - Math.random() * 300000).toISOString(),
      userId: `u-00${(i % 5) + 1}`,
      userName: users[i % 5],
      action: actions[idx],
      module: modules[idx],
      detail: `用户 ${users[i % 5]} 执行了 ${actions[idx]} 操作`,
      ip: `192.168.1.${Math.floor(Math.random() * 254) + 1}`
    })
  }
  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}
