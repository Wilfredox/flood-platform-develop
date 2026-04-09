/**
 * [DEMO-ONLY] Mock 多目标优化数据
 * 生产版本将从 optimization-service 获取真实 NSGA-III 计算结果
 */
import type { ParetoSolution } from '@/types/common'

/** 生成 Mock 帕累托解集（20个非劣解） */
export function generateParetoSolutions(): ParetoSolution[] {
  const solutions: ParetoSolution[] = []

  for (let i = 0; i < 20; i++) {
    // 模拟帕累托前沿：目标之间存在 tradeoff
    const floodBenefit = Math.random() * 0.5 + 0.4
    const powerBenefit = 1 - floodBenefit * 0.6 + (Math.random() - 0.5) * 0.2
    const waterSupply = Math.random() * 0.4 + 0.5
    const eco = 1 - (floodBenefit + powerBenefit) / 3 + Math.random() * 0.2

    solutions.push({
      id: `sol-${String(i + 1).padStart(3, '0')}`,
      floodBenefit: +Math.min(1, Math.max(0, floodBenefit)).toFixed(3),
      powerBenefit: +Math.min(1, Math.max(0, powerBenefit)).toFixed(3),
      waterSupplyBenefit: +Math.min(1, Math.max(0, waterSupply)).toFixed(3),
      ecoBenefit: +Math.min(1, Math.max(0, eco)).toFixed(3),
      isRecommended: i === 7,  // 第8个方案为推荐方案
      schedule: generateSchedule()
    })
  }

  return solutions
}

/** 生成调度过程线 */
function generateSchedule() {
  const schedule = []
  for (let h = 0; h < 72; h += 6) {
    const peakFactor = Math.exp(-((h - 24) ** 2) / 400)
    schedule.push({
      time: `T+${h}h`,
      gateOpening: +(20 + peakFactor * 60 + Math.random() * 5).toFixed(1),
      discharge: +(500 + peakFactor * 4500 + Math.random() * 200).toFixed(0)
    })
  }
  return schedule
}
