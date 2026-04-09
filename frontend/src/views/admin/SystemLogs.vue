<script setup lang="ts">
/**
 * M03 系统日志 · 只读表格
 * [DEMO-ONLY] Mock 日志数据，支持关键字搜索
 */
import { ref, computed } from 'vue'
import { generateMockLogs } from '@/mock/logs'
import type { SystemLog } from '@/types/common'

const allLogs = ref<SystemLog[]>(generateMockLogs(50))
const searchKeyword = ref('')

const filteredLogs = computed(() => {
  const kw = searchKeyword.value.toLowerCase()
  if (!kw) return allLogs.value
  return allLogs.value.filter(log =>
    log.userName.includes(kw) ||
    log.action.includes(kw) ||
    log.module.includes(kw) ||
    log.detail.includes(kw)
  )
})

// 分页
const currentPage = ref(1)
const pageSize = ref(15)
const pagedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredLogs.value.slice(start, start + pageSize.value)
})

function formatTime(ts: string) {
  return new Date(ts).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="system-logs">
    <div class="page-toolbar">
      <h3 style="color: var(--text-primary); margin: 0;">系统日志</h3>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户/操作/模块..."
        clearable
        style="width: 300px;"
      />
    </div>

    <el-table :data="pagedLogs" stripe style="width: 100%;"
      :header-cell-style="{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderColor: 'var(--border-color)' }"
      :cell-style="{ background: 'transparent', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
    >
      <el-table-column prop="id" label="ID" width="90" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
      </el-table-column>
      <el-table-column prop="userName" label="用户" width="120" />
      <el-table-column prop="module" label="模块" width="120" />
      <el-table-column prop="action" label="操作" width="140" />
      <el-table-column prop="detail" label="详情" min-width="240" />
      <el-table-column prop="ip" label="IP 地址" width="140" />
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="filteredLogs.length"
      layout="total, prev, pager, next"
      small
      style="margin-top: 12px; justify-content: flex-end;"
    />
  </div>
</template>

<style scoped>
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-bg-color: var(--bg-tertiary);
}
</style>
