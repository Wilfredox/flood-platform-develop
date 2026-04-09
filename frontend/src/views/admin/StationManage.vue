<script setup lang="ts">
/**
 * M03 站点管理 · CRUD 页面
 * [DEMO-ONLY] 数据存储在 Pinia，刷新后重置
 */
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { mockStations } from '@/mock/station'
import type { StationInfo } from '@/types/station'

// 表格数据（响应式副本）
const tableData = ref<StationInfo[]>([...mockStations])

// 弹窗控制
const dialogVisible = ref(false)
const dialogTitle = ref('新增站点')
const isEdit = ref(false)

const form = reactive<StationInfo>({
  id: '', name: '', basinId: '', basinName: '',
  type: 'water_level', lng: 0, lat: 0, status: 'online'
})

// 搜索
const searchKeyword = ref('')
const filteredData = ref<StationInfo[]>([])

function doSearch() {
  const kw = searchKeyword.value.toLowerCase()
  filteredData.value = kw
    ? tableData.value.filter(s => s.name.includes(kw) || s.basinName.includes(kw))
    : [...tableData.value]
}

function resetForm() {
  Object.assign(form, { id: '', name: '', basinId: '', basinName: '', type: 'water_level', lng: 0, lat: 0, status: 'online' })
}

function handleAdd() {
  resetForm()
  dialogTitle.value = '新增站点'
  isEdit.value = false
  dialogVisible.value = true
}

function handleEdit(row: StationInfo) {
  Object.assign(form, { ...row })
  dialogTitle.value = '编辑站点'
  isEdit.value = true
  dialogVisible.value = true
}

function handleSave() {
  if (!form.name) { ElMessage.warning('请输入站点名称'); return }

  if (isEdit.value) {
    const idx = tableData.value.findIndex(s => s.id === form.id)
    if (idx >= 0) tableData.value[idx] = { ...form }
    ElMessage.success('站点已更新')
  } else {
    form.id = `stn-${String(tableData.value.length + 1).padStart(3, '0')}`
    tableData.value.push({ ...form })
    ElMessage.success('站点已新增')
  }
  dialogVisible.value = false
  doSearch()
}

function handleDelete(row: StationInfo) {
  ElMessageBox.confirm(`确定删除站点「${row.name}」？`, '提示', { type: 'warning' })
    .then(() => {
      tableData.value = tableData.value.filter(s => s.id !== row.id)
      ElMessage.success('已删除')
      doSearch()
    })
    .catch(() => {})
}

// 初始化
doSearch()
</script>

<template>
  <div class="station-manage">
    <!-- 工具栏 -->
    <div class="page-toolbar">
      <el-input v-model="searchKeyword" placeholder="搜索站点名称/流域..." clearable style="width: 260px;" @input="doSearch" />
      <el-button type="primary" @click="handleAdd">+ 新增站点</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="filteredData" stripe style="width: 100%;"
      :header-cell-style="{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderColor: 'var(--border-color)' }"
      :cell-style="{ background: 'transparent', color: 'var(--text-primary)', borderColor: 'var(--border-color)' }"
    >
      <el-table-column prop="id" label="编号" width="100" />
      <el-table-column prop="name" label="站点名称" width="180" />
      <el-table-column prop="basinName" label="所属流域" width="120" />
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          {{ row.type === 'water_level' ? '水位站' : row.type === 'rainfall' ? '雨量站' : '流量站' }}
        </template>
      </el-table-column>
      <el-table-column prop="lng" label="经度" width="100" />
      <el-table-column prop="lat" label="纬度" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'online' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
            {{ row.status === 'online' ? '在线' : row.status === 'warning' ? '预警' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button text type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="站点名称">
          <el-input v-model="form.name" placeholder="如：武汉关水文站" />
        </el-form-item>
        <el-form-item label="所属流域">
          <el-select v-model="form.basinName" placeholder="选择流域">
            <el-option label="长江流域" value="长江流域" />
            <el-option label="淮河流域" value="淮河流域" />
            <el-option label="太湖流域" value="太湖流域" />
          </el-select>
        </el-form-item>
        <el-form-item label="站点类型">
          <el-select v-model="form.type">
            <el-option label="水位站" value="water_level" />
            <el-option label="雨量站" value="rainfall" />
            <el-option label="流量站" value="flow" />
          </el-select>
        </el-form-item>
        <el-form-item label="经度">
          <el-input-number v-model="form.lng" :min="73" :max="135" :precision="2" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input-number v-model="form.lat" :min="18" :max="54" :precision="2" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="在线" value="online" />
            <el-option label="预警" value="warning" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
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

:deep(.el-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
}

:deep(.el-dialog__body) {
  color: var(--text-primary);
}
</style>
