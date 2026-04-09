/**
 * M09 智能体 Mock 数据
 * [DEMO-ONLY] 模拟 Agentic 智能体的对话响应
 * 智能体根据当前防汛态势，返回专业的分析与建议
 */

export interface AgentMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  timestamp: string
  /** 智能体类型标记 */
  agentType?: 'flood-analysis' | 'alert-decision' | 'optimization' | 'emergency' | 'query' | 'report'
}

/** 智能体快捷指令 */
export interface QuickCommand {
  label: string
  icon: string
  prompt: string
  agentType: AgentMessage['agentType']
}

/** 预设快捷指令 */
export const quickCommands: QuickCommand[] = [
  {
    label: '当前汛情研判',
    icon: '🌊',
    prompt: '请分析当前流域的实时汛情态势',
    agentType: 'flood-analysis'
  },
  {
    label: '预警建议',
    icon: '⚠️',
    prompt: '根据最新预报数据，给出预警等级建议',
    agentType: 'alert-decision'
  },
  {
    label: '优化调度方案',
    icon: '⚙️',
    prompt: '请生成当前条件下的最优水库调度方案',
    agentType: 'optimization'
  },
  {
    label: '生成防汛简报',
    icon: '📋',
    prompt: '请生成今日防汛态势简报',
    agentType: 'report'
  }
]

/** 模拟智能体响应库 —— 根据用户输入关键词匹配 */
const responseMap: Record<string, { content: string; agentType: AgentMessage['agentType'] }> = {
  '汛情|水情|态势|研判|分析': {
    agentType: 'flood-analysis',
    content: `**【洪水研判智能体】当前汛情态势分析**

📊 综合判断：当前流域处于 **主汛期偏强阶段**

**关键指标：**
- 淮河干流王家坝站水位 24.35m，距警戒水位（27.5m）尚余 3.15m
- 上游 6h 累计降雨量 45.2mm，预计未来 12h 还将增加 30~50mm
- 当前流量 3,200 m³/s，洪峰预计 8~12 小时后到达

**洪水类型：** 暴雨型河道洪水，预估量级约 20 年一遇

**建议：**
1. 密切关注上游雨量站数据变化
2. 预调度下游水库腾库 1,500 万 m³
3. 如水位超 26.0m，建议启动 **黄色预警**`
  },

  '预警|告警|等级|建议': {
    agentType: 'alert-decision',
    content: `**【预警决策智能体】分级预警建议**

基于实时预报与历史统计分析：

| 区域 | 建议等级 | 依据 |
|------|---------|------|
| 王家坝—鲁台子段 | 🟡 黄色预警 | 预报水位接近警戒，24h 超警概率 35% |
| 正阳关段 | 🔵 蓝色预警 | 水位平稳上涨，暂无超警风险 |
| 蚌埠闸上游 | 🟡 黄色预警 | 承接上游来水，叠加区间暴雨 |

**建议措施：**
1. 黄色预警区启动 24h 值班制度
2. 通知沿岸乡镇做好转移准备
3. 蚌埠闸开闸预泄，提前降低上游水位 0.5m`
  },

  '调度|优化|方案|水库': {
    agentType: 'optimization',
    content: `**【优化调度智能体】多目标调度方案推荐**

已调用 NSGA-II 多目标优化引擎，生成 3 个帕累托最优方案：

**🏆 推荐方案（方案 B — 均衡型）：**

| 时段 | 闸门开度 | 泄流量 | 下游水位预测 |
|------|---------|--------|------------|
| 08:00-12:00 | 45% | 1,800 m³/s | 23.1m |
| 12:00-18:00 | 60% | 2,400 m³/s | 24.5m |
| 18:00-24:00 | 35% | 1,400 m³/s | 23.8m |

**优化目标达成：**
- 🛡️ 防洪安全：下游不超警概率 92%
- 💧 供水保障：保持最低生态流量 800 m³/s
- ⚡ 发电效益：预计发电量 12.8 万 kWh

> 当前推荐以防洪为首要目标，兼顾经济效益。请指挥长审批后执行。`
  },

  '简报|报告|总结|复盘': {
    agentType: 'report',
    content: `**【报告生成智能体】今日防汛态势简报**

**${new Date().toLocaleDateString('zh-CN')} 防汛日报**

---

**一、雨情概况**
全流域 24h 面平均降雨量 32.5mm，最大站点降雨 68.2mm（霍山站）。降雨主要集中在流域上游，呈西南→东北推移趋势。

**二、水情概况**
- 监测站点 15 个，正常 12 个，预警 2 个，离线 1 个
- 干流王家坝站今日最高水位 24.35m（08:00），水势上涨
- 蚌埠闸今日平均流量 2,100 m³/s

**三、调度执行情况**
- 佛子岭水库：拦蓄洪量 800 万 m³，当前蓄水率 78%
- 磨子潭水库：预泄 200 万 m³，为洪峰过境腾出库容

**四、明日研判**
预计明日流域仍有中到大雨，王家坝站水位将继续上涨至 25.5~26.0m，需持续关注。`
  }
}

/** 匹配用户消息，返回智能体响应 */
function matchResponse(input: string): { content: string; agentType: AgentMessage['agentType'] } {
  for (const [pattern, response] of Object.entries(responseMap)) {
    const regex = new RegExp(pattern, 'i')
    if (regex.test(input)) {
      return response
    }
  }
  // 默认通用回复
  return {
    agentType: 'query',
    content: `**【智能助手】**

收到您的问题："${input}"

我可以为您提供以下服务：
- 🌊 **汛情研判** — 综合分析当前水雨情态势
- ⚠️ **预警建议** — 给出分区分级预警建议
- ⚙️ **调度优化** — 生成多目标最优调度方案
- 📋 **简报生成** — 自动撰写防汛态势简报

请尝试上方快捷指令，或直接描述您的需求。`
  }
}

let msgId = 0
function genId(): string {
  return `msg-${Date.now()}-${++msgId}`
}

function now(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

/** 模拟智能体回复（带打字延迟） */
export function mockAgentReply(userInput: string): Promise<AgentMessage> {
  const { content, agentType } = matchResponse(userInput)
  const delay = 600 + Math.random() * 800 // 600~1400ms 模拟思考
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        id: genId(),
        role: 'agent',
        content,
        timestamp: now(),
        agentType
      })
    }, delay)
  })
}

/** 创建用户消息对象 */
export function createUserMessage(content: string): AgentMessage {
  return {
    id: genId(),
    role: 'user',
    content,
    timestamp: now()
  }
}

/** 系统欢迎语 */
export function getWelcomeMessage(): AgentMessage {
  return {
    id: genId(),
    role: 'system',
    content: '🤖 防汛智能体已就绪，可随时分析汛情、生成预警建议或优化调度方案。',
    timestamp: now()
  }
}
