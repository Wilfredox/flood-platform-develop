# 技能矩阵 · Skill Matrix

> 记录本项目所需的全部技术栈及当前掌握/使用状态，用于指导开发决策。

---

## 前端技术栈

| 技术 | 版本 | 用途 | Demo 阶段状态 | 备注 |
|------|------|------|--------------|------|
| Vue 3 | 3.4+ | 前端框架 | ✅ 使用中 | Composition API + `<script setup>` |
| Vite | 5.x | 构建工具 | ✅ 使用中 | 快速 HMR |
| TypeScript | 5.x | 类型系统 | ✅ 使用中 | 严格模式 |
| Element Plus | 2.x | UI 组件库 | ✅ 使用中 | 后台管理 + 表单 |
| ECharts | 5.x | 图表可视化 | ✅ 使用中 | 折线图/散点图/仪表盘 |
| Leaflet.js | 1.9 | 二维地图 | ✅ Demo 使用 | 底图切换为天地图 API |
| Cesium.js | 1.x | 三维 GIS | ⏳ Phase-4 | 数字孪生三维场景 |
| Pinia | 2.x | 状态管理 | ✅ 使用中 | 替代 Vuex |
| Vue Router | 4.x | 路由 | ✅ 使用中 | 嵌套路由 |
| Axios | 1.x | HTTP 客户端 | ✅ 使用中 | 统一拦截 |
| v-scale-screen | - | 大屏适配 | ✅ 使用中 | 1920×1080 等比缩放 |
| D3.js | 7.x | 高级图形 | ⏳ Phase-3 | 帕累托前沿 |
| SockJS + STOMP.js | - | WebSocket | 🔶 Mock 中 | setInterval 模拟 |

## 后端技术栈

| 技术 | 版本 | 用途 | Demo 阶段状态 | 备注 |
|------|------|------|--------------|------|
| Spring Boot | 3.x | 微服务基础 | ✅ 使用中 | JDK 17+ |
| Spring Cloud | 2023 | 微服务治理 | ⏳ Phase-2 | Demo 单体运行 |
| Spring Security | 6.x | 认证授权 | 🔶 简化版 | JWT + 内存用户 |
| MyBatis-Plus | 3.x | ORM | ⏳ Phase-2 | Demo 用内存 Map |
| Nacos | 2.3 | 服务注册 | ⏳ Phase-2 | Docker Compose |
| Spring Gateway | - | API 网关 | ⏳ Phase-2 | Demo 直连 |
| Kafka | 3.6 | 消息队列 | 🔶 Mock 中 | LinkedBlockingQueue |
| Flink | - | 流处理 | ⏳ Phase-2 | 暂不引入 |

## AI / 优化技术栈

| 技术 | 版本 | 用途 | Demo 阶段状态 | 备注 |
|------|------|------|--------------|------|
| Python | 3.11 | 运行环境 | ✅ 使用中 | |
| FastAPI | 0.100+ | API 服务 | ✅ 使用中 | 优化 + 预报 |
| PyTorch | 2.x | 深度学习 | ⏳ Phase-4 | LSTM/Transformer |
| pymoo | 0.6+ | 多目标优化 | ⏳ Phase-3 | NSGA-III |
| NumPy / Pandas | - | 数值计算 | ✅ 使用中 | Mock 数据生成 |

## 数据存储

| 技术 | 版本 | 用途 | Demo 阶段状态 | 备注 |
|------|------|------|--------------|------|
| InfluxDB | 2.7 | 时序数据 | 🔶 H2 替代 | Docker 可选 |
| PostgreSQL | 15 | 业务数据 | 🔶 H2 替代 | Docker 可选 |
| Redis | 7 | 缓存 | 🔶 内存 Map | Docker 可选 |
| MinIO | - | 对象存储 | ⏳ Phase-3 | |
| Elasticsearch | 8.x | 日志搜索 | ⏳ Phase-3 | |

## 基础设施

| 技术 | 版本 | 用途 | Demo 阶段状态 | 备注 |
|------|------|------|--------------|------|
| Docker | 24+ | 容器化 | 🔶 中间件 | docker-compose |
| Kubernetes | - | 容器编排 | ⏳ Phase-5 | Helm 部署 |
| Jenkins / GitLab CI | - | CI/CD | ⏳ Phase-3 | |
| Git | - | 版本控制 | ✅ 使用中 | 分支策略完整 |

---

### 图例

| 符号 | 含义 |
|------|------|
| ✅ | 已启用/正在使用 |
| 🔶 | 简化/Mock 模式运行 |
| ⏳ | 计划在后续阶段引入 |
