<script setup lang="ts">
/**
 * M03 预警规则配置
 * [DEMO-ONLY] 4级阈值 × 3项指标 配置表单
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

interface AlertRuleRow {
  stationName: string
  metric: string
  metricUnit: string
  blue: number
  yellow: number
  orange: number
  red: number
  enabled: boolean
}

const rules = ref<AlertRuleRow[]>([
  { stationName: '武汉关水文站', metric: '水位', metricUnit: 'm', blue: 24.0, yellow: 25.0, orange: 26.5, red: 28.0, enabled: true },
  { stationName: '武汉关水文站', metric: '雨量', metricUnit: 'mm/h', blue: 10, yellow: 25, orange: 40, red: 60, enabled: true },
  { stationName: '武汉关水文站', metric: '流量', metricUnit: 'm³/s', blue: 3000, yellow: 4500, orange: 5800, red: 7000, enabled: true },
  { stationName: '九江水文站', metric: '水位', metricUnit: 'm', blue: 22.0, yellow: 23.5, orange: 25.0, red: 26.5, enabled: true },
  { stationName: '九江水文站', metric: '雨量', metricUnit: 'mm/h', blue: 10, yellow: 25, orange: 40, red: 60, enabled: true },
  { stationName: '九江水文站', metric: '流量', metricUnit: 'm³/s', blue: 2500, yellow: 3800, orange: 5000, red: 6500, enabled: false },
  { stationName: '正阳关水文站', metric: '水位', metricUnit: 'm', blue: 23.0, yellow: 24.5, orange: 26.0, red: 27.5, enabled: true },
  { stationName: '正阳关水文站', metric: '雨量', metricUnit: 'mm/h', blue: 10, yellow: 25, orange: 40, red: 60, enabled: true },
])

function handleSave() {
  // [DEMO-ONLY] 保存到内存
  ElMessage.success('预警规则已保存（Demo 模式：仅内存存储）')
}

function toggleEnabled(row: AlertRuleRow) {
  row.enabled = !row.enabled
  ElMessage.info(`${row.stationName} ${row.metric} 规则已${row.enabled ? '启用' : '禁用'}`)
}
</script>

<template>
  <div class="alert-rule-config">
    <div class="page-toolbar">
      <h3 style="color: var(--text-primary); margin: 0;">预警规则配置</h3>
      <el-button type="primary" @click="handleSave">💾 保存全部</el-button>
    </div>

    <el-table :data="rules" stripe style="width: 100%;"
      :header-cell-style="{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderColor: 'var(--border-color)' }"
      :cell-style="{ background: 'transparent', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
    >
      <el-table-column prop="stationName" label="站点" width="160" />
      <el-table-column prop="metric" label="指标" width="80" />
      <el-table-column label="蓝色(关注)" width="130">
        <template #default="{ row }">
          <el-input-number v-model="row.blue" :precision="1" size="small" controls-position="right" style="width: 100px;" />
        </template>
      </el-table-column>
      <el-table-column label="黄色(预警)" width="130">
        <template #default="{ row }">
          <el-input-number v-model="row.yellow" :precision="1" size="small" controls-position="right" style="width: 100px;" />
        </template>
      </el-table-column>
      <el-table-column label="橙色(警告)" width="130">
        <template #default="{ row }">
          <el-input-number v-model="row.orange" :precision="1" size="small" controls-position="right" style="width: 100px;" />
        </template>
      </el-table-column>
      <el-table-column label="红色(紧急)" width="130">
        <template #default="{ row }">
          <el-input-number v-model="row.red" :precision="1" size="small" controls-position="right" style="width: 100px;" />
        </template>
      </el-table-column>
      <el-table-column prop="metricUnit" label="单位" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="() => {}" />
        </template>
      </el-table-column>
    </el-table>

    <div class="config-note">
      <p>📌 规则说明：当监测值达到或超过对应阈值时，系统自动触发对应等级的预警。</p>
      <p>📌 阈值关系：蓝色 &lt; 黄色 &lt; 橙色 &lt; 红色（数值递增）。</p>
    </div>
  </div>
</template>

<style scoped>
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.config-note {
  margin-top: 20px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-tertiary);
  line-height: 1.8;
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  --el-table-row-hover-bg-color: var(--bg-tertiary);
}
</style>
