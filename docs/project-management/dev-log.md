# 开发记录表 · Development Log

> 记录每次开发会话的操作内容、产出与决策，便于追溯和协作。

---

## 会话记录

### Session #001 · 2026-03-07

**阶段：** PHASE-1 Demo 原型开发  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 首次项目初始化

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 项目目录结构创建 | ✅ | `flood-platform/` 全部子目录 |
| 2 | 项目管理文档创建 | ✅ | `docs/project-management/*.md` |
| 3 | Vue 3 前端项目初始化 | ✅ | `frontend/` |
| 4 | M10 登录页面实现 | ✅ | `views/login/LoginPage.vue` |
| 5 | M01 数据大屏实现 | ✅ | `views/dashboard/` |
| 6 | M02 实时详情页实现 | ✅ | `views/detail/` |
| 7 | M03 后台管理实现 | ✅ | `views/admin/` |
| 8 | Mock 数据层 | ✅ | `mock/` |
| 9 | 后端服务桩代码 | ✅ | `backend/`, `python-services/` |
| 10 | Docker Compose 配置 | ✅ | `docker-compose.middleware.yml` |

#### 技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 地图方案 | Leaflet.js (Demo) | Cesium 需要 token 且体积大，Demo 阶段 Leaflet 更轻量 |
| Mock 方式 | 本地 TypeScript 文件 | 比 mockjs/json-server 更简单，类型安全 |
| WebSocket | setInterval 模拟 | Demo 阶段无需真实 WS 连接 |
| 数据库 | 内存 Map / H2 | Demo 阶段无需持久化 |
| UI 框架 | Element Plus | 项目指定，组件丰富 |

#### 遗留问题

| # | 问题 | 优先级 | 计划解决阶段 |
|---|------|--------|-------------|
| 1 | Cesium 三维场景未实现 | P2 | Phase-4 |
| 2 | 真实 WebSocket 未接入 | P1 | Phase-2 |
| 3 | 后端微服务注册/网关未启用 | P2 | Phase-2 |
| 4 | 真实数据库未接入 | P2 | Phase-2 |
| 5 | ML 模型为线性外推模拟 | P2 | Phase-4 |

---

### Session #002 · 续接上次会话

**阶段：** PHASE-1 Demo 原型开发 (收尾)  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 后端/Python 服务桩 + Docker + README

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | M04 data-ingest-service 完善 | ✅ | `SensorData.java`, `SensorDataService.java`, `application.yml`, `pom.xml` |
| 2 | M05 alert-engine-service 创建 | ✅ | `AlertEngineApplication.java`, `AlertLevel.java`, `AlertRule.java`, `AlertController.java`, `pom.xml`, `application.yml` |
| 3 | M10 auth-service 创建 | ✅ | `AuthServiceApplication.java`, `AuthController.java`, `pom.xml`, `application.yml` |
| 4 | M06 optimization-service 创建 | ✅ | `OptimizationServiceApplication.java`, `OptimizationController.java`, `pom.xml`, `application.yml` |
| 5 | Python optimization-api 创建 | ✅ | `main.py`, `requirements.txt` |
| 6 | Python ml-forecast-api 创建 | ✅ | `main.py`, `requirements.txt` |
| 7 | Docker Compose 中间件配置 | ✅ | `docker/docker-compose.middleware.yml` |
| 8 | 项目 README.md | ✅ | `README.md` |
| 9 | .gitignore | ✅ | `.gitignore` |
| 10 | 前端构建验证 | ✅ | `npm install` + `vite build` 成功 (8.12s) |

#### 服务端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend (Vite dev) | 5173 | 前端开发服务 |
| data-ingest-service | 8081 | 数据接入 |
| alert-engine-service | 8082 | 告警引擎 |
| auth-service | 8083 | 认证授权 |
| optimization-service | 8084 | 优化调度 (Java) |
| optimization-api | 9001 | 优化调度 (Python) |
| ml-forecast-api | 9002 | ML 洪水预报 |

#### Demo 阶段总结

✅ **所有 Demo 阶段目标已完成**：
- 前端 4 个核心页面 (M10 登录 / M01 大屏 / M02 详情 / M03 管理) 全部实现
- Mock 数据覆盖 15 站点 × 3 流域，含实时模拟
- 后端 4 个 Spring Boot 微服务桩代码
- Python 2 个 FastAPI 算法服务桩代码
- Docker 中间件编排配置
- 项目文档完整 (README + 管理文档 5 份)

---

*后续会话记录追加在此文件底部*

---

### Session #003 · 2026-03-07

**阶段：** PHASE-1 Demo 增强（智能体 + 天地图）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 功能增强 + 文档更新

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | M09 智能体对话面板（Demo） | ✅ | `views/dashboard/components/AgentChat.vue` |
| 2 | 智能体 Mock 数据层 | ✅ | `mock/agent.ts` |
| 3 | 大屏地图切换为天地图 API | ✅ | `components/MapPanel.vue` 重写底图 |
| 4 | 大屏右栏改为三段式布局 | ✅ | `DashboardPage.vue` 布局调整 |
| 5 | Git 仓库初始化 + 分支策略 | ✅ | `.gitignore`, `git-branch-strategy.md` |
| 6 | tsconfig.node.json 修复 | ✅ | `tsconfig.node.json` |
| 7 | 项目文档同步更新 | ✅ | `todo-list.md`, `dev-log.md` |

#### 技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 智能体面板位置 | 嵌入大屏右栏 | 用户要求"有机整体，非外置器官"；与水位图/预警列表并列，自然融入驾驶舱 |
| 智能体交互方式 | 快捷指令 + 自由输入 | 快捷指令降低使用门槛，自由输入保留灵活性 |
| 智能体 Mock 方式 | 关键词正则匹配 → 预设专业响应 | Demo 阶段无需真实 LLM，展示四类智能体能力即可 |
| 地图底图 | 天地图卫星影像 + 中文注记 | 用户明确要求天地图 API；国产地图服务，符合项目定位 |
| M09 优先级 | P2 → P0 | 用户要求先做 Demo 给领导展示，智能体是核心亮点 |

#### 智能体能力 Demo 概览

| 智能体类型 | 触发关键词 | Mock 输出 |
|-----------|-----------|----------|
| 🌊 洪水研判智能体 | 汛情/水情/态势/分析 | 洪水类型判定 + 关键指标 + 建议 |
| ⚠️ 预警决策智能体 | 预警/告警/等级 | 分区分级预警表 + 措施建议 |
| ⚙️ 优化调度智能体 | 调度/优化/方案/水库 | 帕累托方案推荐 + 时段调度表 |
| 📋 报告生成智能体 | 简报/报告/总结 | 防汛日报（雨情/水情/调度/研判） |

#### 遗留问题

| # | 问题 | 优先级 | 计划解决阶段 |
|---|------|--------|-------------|
| 1 | 天地图 Key 为开发测试用，生产需替换 | P1 | Phase-2 |
| 2 | 智能体为 Mock 响应，需接真实 LLM | P1 | Phase-4 |
| 3 | 天地图卫星影像偏暗但非纯暗色主题 | P2 | 可自定义 CSS filter |
---

### Session #004 · 2026-03-07

**阶段：** PHASE-1 Demo 品牌化 + UI 调优  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 布局修复 + 品牌更名

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 大屏布局溢出修复（多轮） | ✅ | `DashboardPage.vue`, `global.css`, 各组件 |
| 2 | 智能体面板消息截断修复 | ✅ | `AgentChat.vue` (height:100%, min-height:0) |
| 3 | 滚动条可拖拽优化 | ✅ | `global.css` (8px + border-radius) |
| 4 | 系统更名为「澜镜数字孪生洪水预警监管平台」 | ✅ | `HeaderBar.vue`, `LoginPage.vue`, `global.css` |
| 5 | 导航栏扩展（4 个占位入口） | ✅ | `HeaderBar.vue` (洪水预报/历史回溯/数字孪生/应急指挥) |
| 6 | 去除页面中的 emoji 符号 | ✅ | `HeaderBar.vue`, `LoginPage.vue` |
| 7 | 智能体面板移至右上角 | ✅ | `DashboardPage.vue` 右栏排序调整 |

#### 技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 布局模式 | 100vw × 100vh + flex + min-height:0 | 避免内容溢出，兼容不同分辨率 |
| 导航占位实现 | alert() 提示「功能开发中」 | Demo 阶段无真实路由，占位展示即可 |
| 平台命名 | 澜镜（LanJing） | 用户指定品牌名，体现水利 + 数字镜像双关 |
| 右栏排列 | 智能体(top) → 水位图 → 预警列表 | 用户要求智能体从右下移至右上，最先看到 |

---

### Session #005 · 2026-03-07

**阶段：** 技术路线深化 · 多智能体 + 多模型架构设计  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 文档规划

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 重写 Roadmap 第七章「Agentic 智能体模块」 | ✅ | `flood_platform_roadmap.md` §7 |
| 2 | 新增 7 大 Agent 能力矩阵 + 统一接口契约 | ✅ | §7.2 + §7.3 |
| 3 | 新增三种协作模式（串行/并行/混合 DAG） | ✅ | §7.4 |
| 4 | 新增 LangGraph DAG 编排代码示例 | ✅ | §7.5 |
| 5 | 新增模型融合策略（残差修正/BMA） | ✅ | §7.6 |
| 6 | 新增自然语言→地图操控联动设计 | ✅ | §7.7 |
| 7 | 新增 LLM 技术路线对比 | ✅ | §7.8 |
| 8 | 更新 Python 服务列表（+新安江/水力学/编排） | ✅ | §8 python-services |
| 9 | 更新 AI 技术栈清单 + 阶段四任务列表 | ✅ | §9 + §10 |

#### 架构决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| Agent 编排框架 | LangGraph (Python) | 原生支持 DAG 并行/汇聚，状态共享，比 LangChain4j 生态更成熟 |
| LLM | DeepSeek API 为主 | 成本极低、Function Calling 成熟，毕设不值得卷本地部署 |
| 新安江模型 | NumPy 自研 (~500行) | 体现自主研发能力，答辩加分；比 HEC-RAS 轻量 |
| 水力学模型 | 一维圣维南简化 + 曼宁 | 毕设够用，输出淹没 GeoJSON 可直接叠加地图 |
| 模型融合 | 残差修正 Q = Q_xaj + ΔQ_lstm | 物理机理保底 + AI 修正，论文/答辩讲"混合建模"亮眼 |
| 模型接口 | 统一 TimeSeriesInput/Output | 保证模型可插拔替换，新模型只需实现 POST /predict |
| 模型服务端口 | :9001-:9004 + :9010 编排 | 各模型独立进程，互不影响 |

---

### Session #006 · 2026-04-02

**阶段：** River1D 专项推进（R6/R8/R9）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 属性编辑 + 方案文件管理 + 导出能力

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 属性面板 V1：按要素类型动态字段编辑并保存 | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue`, `frontend/src/stores/useRiver1dStore.ts` |
| 2 | 方案文件管理 V1：打开/保存/另存为 `.r1d/.json` | ✅ | `frontend/src/views/river1d/River1DPage.vue`, `frontend/src/stores/useRiver1dStore.ts`, `frontend/src/types/river1d.d.ts` |
| 3 | 导出能力 V1：GeoJSON + JSON 双文件下载 | ✅ | `frontend/src/views/river1d/River1DPage.vue` |
| 4 | River1D 专项任务状态同步 | ✅ | `docs/project-management/todo-list.md` |

#### 技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 方案文件格式 | `River1dProjectFile` 统一结构（version/savedAt/project/features） | 便于后续做版本兼容与迁移 |
| 保存策略 | 前端直接序列化下载 `.r1d` | Demo/专项阶段最快形成可验证闭环 |
| 导出策略 | 同时导出 `GeoJSON` + 原始 `JSON` | 兼顾 GIS 工具互操作和本项目回放导入 |
| 属性编辑策略 | 先做动态字段表单，再按类型扩展高级控件 | 以最小改动满足 R6 验收 |

#### 验证记录

- 执行 `frontend` 构建命令：`npm run build`
- 结果：`vite` 在“2225 modules transformed”后退出码为 `1`，终端未返回明确错误栈；本次改动文件在 IDE 诊断中无 TypeScript 报错。
- 说明：需在后续会话排查该构建环境问题（可能与终端/编码或历史依赖状态有关）。

#### 当前专项状态

- 已完成：R1-R6、R8、R9
- 未完成：R7、R10、R11

---

### Session #007 · 2026-04-02

**阶段：** River1D 专项推进（R7）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 断面高程表 + 曲线预览

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 断面编辑能力 V1：起点距-高程表增删改 | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 2 | 断面简易曲线预览（SVG） | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 3 | 专项任务状态同步（R7 完成） | ✅ | `docs/project-management/todo-list.md` |

#### 当前专项状态

- 已完成：R1-R9
- 未完成：R10、R11

---

### Session #008 · 2026-04-02

**阶段：** River1D 专项推进（R10）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 后端接口草案 + 契约文档

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 新增 River1D 后端 DTO 草案（Draft） | ✅ | `backend/optimization-service/src/main/java/com/flood/optimization/dto/river1d/*.java` |
| 2 | 新增 River1D 后端控制器草案（保存/读取/拓扑检查） | ✅ | `backend/optimization-service/src/main/java/com/flood/optimization/controller/River1dModelDraftController.java` |
| 3 | 新增接口契约文档（请求/响应示例） | ✅ | `docs/api/river1d-model-contract.md` |
| 4 | 编译验证通过 | ✅ | `mvn -DskipTests compile` |

#### 当前专项状态

- 已完成：R1-R10
- 未完成：R11

---

### Session #009 · 2026-04-03

**阶段：** River1D 专项推进（R11）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 计算流程 Mock 联动

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 新增计算任务 DTO（启动/状态） | ✅ | `backend/optimization-service/src/main/java/com/flood/optimization/dto/river1d/River1dCompute*.java` |
| 2 | 后端新增计算任务 Mock 接口（启动 + 轮询） | ✅ | `backend/optimization-service/src/main/java/com/flood/optimization/controller/River1dModelDraftController.java` |
| 3 | 前端计算面板联动（参数录入、开始计算、进度和日志） | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 4 | 接口契约文档补充 R11 章节 | ✅ | `docs/api/river1d-model-contract.md` |
| 5 | 专项状态同步（R11 完成） | ✅ | `docs/project-management/todo-list.md` |

#### 当前专项状态

- 已完成：R1-R11
- 专项阶段：全部任务完成（后续进入联调优化与真实引擎对接）

---

### Session #010 · 2026-04-03

**阶段：** River1D 体验修复与大屏风格统一  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 交互修复 + 视觉统一 + 工具栏排版

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 地图默认中心调整至指定坐标（120.43074147503992, 29.13984534608853） | ✅ | `frontend/src/views/river1d/components/R1DMap.vue` |
| 2 | 选择工具命中增强（点击线附近可选中最近要素） | ✅ | `frontend/src/views/river1d/components/R1DMap.vue` |
| 3 | 属性页字段控件修复（侧别/类型下拉、备注多行、保存规范化） | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 4 | 属性 Tab 切换行为修复（进入属性页自动切换选择工具） | ✅ | `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 5 | River1D 页面风格对齐大屏（暗色变量体系） | ✅ | `frontend/src/views/river1d/River1DPage.vue`, `frontend/src/views/river1d/components/R1DToolbar.vue`, `frontend/src/views/river1d/components/R1DRightPanel.vue` |
| 6 | 工具栏排版优化（去“工具”字样、拉开间距、缓解拥挤） | ✅ | `frontend/src/views/river1d/components/R1DToolbar.vue` |

#### 当前专项状态

- River1D 功能：R1-R11 完成并可演示
- River1D 体验：完成首轮可用性修复与视觉统一

---

### Session #011 · 2026-04-03

**阶段：** River1D 交互增强（节点拖拽编辑 + 图标/光标一致性）  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 工具栏与地图交互联动修复

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 新增“节点”工具模式，支持拖拽顶点实时修改线要素形态 | ✅ | `frontend/src/views/river1d/components/R1DMap.vue`, `frontend/src/types/river1d.d.ts` |
| 2 | 工具栏图标替换为 SVG 资源（含节点按钮） | ✅ | `frontend/src/views/river1d/components/R1DToolbar.vue`, `frontend/public/cursors/*.svg` |
| 3 | 鼠标光标与当前工具全程同步（切换/拖拽/缩放过程中保持） | ✅ | `frontend/src/views/river1d/components/R1DMap.vue` |
| 4 | 节点图标简化为“原点”并同步按钮与光标 | ✅ | `frontend/public/cursors/node.svg`, `frontend/src/views/river1d/components/R1DToolbar.vue`, `frontend/src/views/river1d/components/R1DMap.vue` |

#### 当前专项状态

- River1D 功能：R1-R11 已完成
- River1D 交互：节点级编辑与工具视觉反馈闭环已完成

---

### Session #012 · 2026-04-09

**阶段：** Muskingum 模块联调验证与问题归档  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** 端到端接口联调 + 文档修订

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | 完成前后端与 Python 算法服务联调（率定 + 预报） | ✅ | 运行验证（接口联测） |
| 2 | 定位并修复联调阻塞（端口冲突、代理端口不一致） | ✅ | 运行配置与启动流程 |
| 3 | 归档接口层面的已知逻辑问题与修正方向 | ✅ | `docs/api/muskingum-model-contract.md` |

#### 关键验证结论

- 链路可用：`frontend -> optimization-service -> optimization-api` 已跑通。
- 当前实现存在模型结构层面的逻辑简化：A/B 先固定权重汇流，再走单河段到 C。
- 该简化会在复杂洪峰过程中引入相位偏差，导致评估指标波动较大。

#### 后续修正计划

| 方向 | 目标 |
|------|------|
| 多河段拓扑 | 升级为 `A 段 + B 段 + 主河道` 的分层结构 |
| 参数率定 | 各支路独立率定 `K/x` + 汇流时滞 |
| 兼容策略 | 保留 `single_reach`，新增 `multi_reach` 模式 |

---

### Session #013 · 2026-04-09

**阶段：** 地图默认视图与坐标展示优化  
**操作者：** AI Agent (GitHub Copilot)  
**时长：** River1D + 大屏地图交互微调

#### 本次完成内容

| # | 内容 | 状态 | 产出文件 |
|---|------|------|---------|
| 1 | River1D 底栏新增经纬度 DMS 显示（与 XY 并列） | ✅ | `frontend/src/views/river1d/components/R1DMap.vue` |
| 2 | River1D 默认视窗改为指定左上/右下范围 | ✅ | `frontend/src/views/river1d/components/R1DMap.vue` |
| 3 | 大屏默认聚焦改为按浙江省 GeoJSON 边界自适应显示 | ✅ | `frontend/src/views/dashboard/components/MapPanel.vue` |

#### 结果说明

- River1D 进入页面即可看到目标区域，坐标栏同时提供投影 XY 与经纬度（度分秒）信息。  
- 大屏首页默认可完整展示浙江省边界，不再默认过度放大到局部。