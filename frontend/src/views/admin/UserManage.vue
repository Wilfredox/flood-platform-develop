<script setup lang="ts">
/**
 * M03 用户管理页
 * [DEMO-ONLY] Mock 5个用户 + 角色标签
 */
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMockUsers } from '@/mock/auth'
import { RoleLabels } from '@/types/common'
import type { UserInfo, UserRole } from '@/types/common'

const users = ref<UserInfo[]>(getMockUsers())

function roleTagType(role: UserRole): string {
  switch (role) {
    case 'admin': return 'danger'
    case 'province': return 'warning'
    case 'city': return ''
    case 'county': return 'info'
    case 'viewer': return 'info'
    default: return ''
  }
}

function handleResetPassword(user: UserInfo) {
  ElMessageBox.confirm(`确定重置用户「${user.name}」的密码？`, '提示', { type: 'warning' })
    .then(() => {
      ElMessage.success(`用户 ${user.name} 密码已重置为默认密码（Demo 模式）`)
    })
    .catch(() => {})
}

function handleToggleStatus(user: UserInfo) {
  ElMessage.info(`用户 ${user.name} 状态已切换（Demo 模式：仅内存操作）`)
}
</script>

<template>
  <div class="user-manage">
    <div class="page-toolbar">
      <h3 style="color: var(--text-primary); margin: 0;">用户管理</h3>
      <el-button type="primary" disabled>+ 新增用户（开发中）</el-button>
    </div>

    <el-table :data="users" stripe style="width: 100%;"
      :header-cell-style="{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderColor: 'var(--border-color)' }"
      :cell-style="{ background: 'transparent', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="role" label="角色" width="140">
        <template #default="{ row }">
          <el-tag :type="roleTagType(row.role) as any" size="small">
            {{ RoleLabels[row.role as UserRole] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column prop="phone" label="电话" width="140" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="lastLogin" label="最后登录" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="handleResetPassword(row)">重置密码</el-button>
          <el-button text type="warning" size="small" @click="handleToggleStatus(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>
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
</style>
