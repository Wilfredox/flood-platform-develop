# UI/代码风格规范 · Style Guide

> 保持整个项目视觉与代码风格的统一性。

---

## 一、视觉风格规范

### 1.1 配色方案（暗色主题）

```
┌─────────────────────────────────────────────┐
│  数字孪生洪水预报预警平台 · 暗色科技风格      │
└─────────────────────────────────────────────┘
```

| 用途 | 色值 | 变量名 | 说明 |
|------|------|--------|------|
| 主背景色 | `#0d1b2a` | `--bg-primary` | 深蓝黑，大屏背景 |
| 次背景色 | `#1b2838` | `--bg-secondary` | 卡片/面板背景 |
| 三级背景 | `#243447` | `--bg-tertiary` | 悬浮/高亮背景 |
| 主色调 | `#1890FF` | `--color-primary` | 品牌蓝，按钮/链接 |
| 强调色 | `#00D4FF` | `--color-accent` | 数据高亮/图表 |
| 主文字 | `#E8F0FE` | `--text-primary` | 正文白色 |
| 次文字 | `#8BA3C7` | `--text-secondary` | 辅助说明 |
| 三级文字 | `#5A7A9E` | `--text-tertiary` | 标签/占位 |
| 分割线 | `#2A3F55` | `--border-color` | 面板/卡片边框 |
| 成功 | `#52C41A` | `--color-success` | 操作成功/正常 |
| 警告 | `#FAAD14` | `--color-warning` | 黄色预警/注意 |
| 危险 | `#F5222D` | `--color-danger` | 红色预警/错误 |

### 1.2 预警等级配色（国标 GB/T 规范）

| 等级 | 颜色 | 色值 | CSS 类名 |
|------|------|------|---------|
| Ⅳ级（一般） | 蓝色 | `#1890FF` | `.alert-blue` |
| Ⅲ级（较重） | 黄色 | `#FAAD14` | `.alert-yellow` |
| Ⅱ级（严重） | 橙色 | `#FA8C16` | `.alert-orange` |
| Ⅰ级（特别严重） | 红色 | `#F5222D` | `.alert-red` |

### 1.3 字体规范

```css
/* 主字体栈 */
--font-family: 'HarmonyOS Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;

/* 大屏标题字体 */
--font-family-display: 'DIN Alternate', 'Roboto', monospace;

/* 数据数字字体 */
--font-family-number: 'DIN Alternate', 'Roboto Mono', monospace;
```

| 场景 | 字号 | 字重 |
|------|------|------|
| 大屏主标题 | 28px | Bold (700) |
| 大屏副标题 | 18px | Medium (500) |
| 大屏指标数值 | 36px | Bold (700) |
| 卡片标题 | 16px | Medium (500) |
| 正文 | 14px | Regular (400) |
| 辅助文字 | 12px | Regular (400) |

### 1.4 布局规范

| 场景 | 分辨率 | 适配方式 |
|------|--------|---------|
| 数据大屏 | 1920×1080 | v-scale-screen 等比缩放 |
| 后台管理 | 响应式 | Element Plus 栅格 |
| 详情页 | 响应式 | flex 布局 |

```
大屏布局结构：
┌─────────────────────────────────────────────┐
│  顶部标题栏  (height: 80px)                  │
├──────┬────────────────────────┬──────────────┤
│ 左栏  │     中间主区域          │    右栏      │
│ 320px │     自适应              │   380px      │
│       │     (地图/3D)          │              │
│       │                        │              │
├──────┴────────────────────────┴──────────────┤
│  底部指标条  (height: 60px, 可选)              │
└─────────────────────────────────────────────┘
```

---

## 二、代码风格规范

### 2.1 Vue 组件规范

```vue
<!-- 组件模板：统一使用 <script setup lang="ts"> -->
<script setup lang="ts">
// 1. 导入语句（按类别分组，空行分隔）
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { StationInfo } from '@/types/station'

import StationTree from '@/components/StationTree.vue'
import { getStationList } from '@/api/station'

// 2. Props & Emits
interface Props {
  stationId: string
  showChart?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  showChart: true
})

const emit = defineEmits<{
  (e: 'select', id: string): void
}>()

// 3. 响应式状态
const loading = ref(false)
const stationList = ref<StationInfo[]>([])

// 4. 计算属性
const activeStation = computed(() =>
  stationList.value.find(s => s.id === props.stationId)
)

// 5. 方法
function handleSelect(id: string) {
  emit('select', id)
}

// 6. 生命周期
onMounted(async () => {
  loading.value = true
  stationList.value = await getStationList()
  loading.value = false
})
</script>

<template>
  <!-- 模板部分 -->
</template>

<style scoped>
/* 局部样式 */
</style>
```

### 2.2 命名规范

| 类型 | 命名方式 | 示例 |
|------|---------|------|
| 组件文件 | PascalCase | `WaterLevelChart.vue` |
| 组合函数 | camelCase + use 前缀 | `useWaterLevel.ts` |
| API 接口文件 | camelCase | `stationApi.ts` |
| 类型文件 | camelCase | `station.d.ts` |
| CSS 变量 | kebab-case | `--bg-primary` |
| Pinia Store | camelCase + use 前缀 | `useAlertStore.ts` |
| Mock 数据文件 | camelCase | `stationMock.ts` |
| 路由名称 | kebab-case | `detail-page` |

### 2.3 目录结构规范（前端）

```
src/
├── api/                # 接口封装（按模块分文件）
│   ├── station.ts
│   ├── alert.ts
│   └── optimization.ts
├── assets/             # 静态资源
│   ├── images/
│   └── styles/
│       ├── variables.css    # CSS 变量定义
│       ├── global.css       # 全局样式
│       └── dashboard.css    # 大屏专用样式
├── components/         # 通用组件
│   ├── charts/         # 图表组件
│   ├── common/         # 基础通用组件
│   └── layout/         # 布局组件
├── mock/               # Mock 数据
│   ├── station.ts
│   ├── alert.ts
│   └── optimization.ts
├── router/             # 路由配置
│   └── index.ts
├── stores/             # Pinia 状态管理
│   ├── useAuthStore.ts
│   ├── useAlertStore.ts
│   └── useStationStore.ts
├── types/              # TypeScript 类型定义
│   ├── station.d.ts
│   ├── alert.d.ts
│   └── common.d.ts
├── utils/              # 工具函数
│   ├── request.ts      # Axios 封装
│   ├── format.ts       # 格式化工具
│   └── constants.ts    # 常量定义
└── views/              # 页面级组件
    ├── dashboard/      # M01 数据大屏
    ├── detail/         # M02 实时详情
    ├── admin/          # M03 后台管理
    └── login/          # M10 登录页
```

### 2.4 注释规范

```typescript
/**
 * [DEMO-ONLY] 此处使用 Mock 数据，生产版本需替换为真实接口
 * @see docs/api/M01-接口契约.yaml
 */

// 关键业务逻辑必须注释说明
// 预警等级判定：水位超警戒线 → 根据超出幅度分级
function evaluateAlertLevel(waterLevel: number, threshold: number): AlertLevel {
  const ratio = waterLevel / threshold
  if (ratio >= 1.5) return 'RED'      // 超 50%：红色预警
  if (ratio >= 1.2) return 'ORANGE'   // 超 20%：橙色预警
  if (ratio >= 1.0) return 'YELLOW'   // 刚超过：黄色预警
  return 'BLUE'                        // 未超过：蓝色（正常关注）
}
```

---

## 三、ECharts 图表风格统一

```typescript
// 统一暗色主题配置
export const darkThemeConfig = {
  backgroundColor: 'transparent',
  textStyle: {
    color: '#8BA3C7',
    fontFamily: 'HarmonyOS Sans, PingFang SC, sans-serif'
  },
  title: {
    textStyle: { color: '#E8F0FE', fontSize: 16 }
  },
  legend: {
    textStyle: { color: '#8BA3C7' }
  },
  xAxis: {
    axisLine: { lineStyle: { color: '#2A3F55' } },
    axisLabel: { color: '#8BA3C7' },
    splitLine: { lineStyle: { color: '#1B2838' } }
  },
  yAxis: {
    axisLine: { lineStyle: { color: '#2A3F55' } },
    axisLabel: { color: '#8BA3C7' },
    splitLine: { lineStyle: { color: '#1B2838', type: 'dashed' } }
  },
  series: {
    lineStyle: { width: 2 },
    symbolSize: 6
  }
}

// 统一配色序列
export const colorPalette = [
  '#1890FF', '#00D4FF', '#52C41A', '#FAAD14',
  '#FA8C16', '#F5222D', '#722ED1', '#13C2C2'
]
```
