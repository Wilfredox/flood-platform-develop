# 数字孪生洪水预报预警平台 —— Agent 开发提示词系统
## Prompt Engineering Design · Git 分支策略 · 多人协作规范

---

## 目录

1. [提示词设计总体思路](#一提示词设计总体思路)
2. [主提示词（Master Prompt）](#二主提示词master-prompt)
3. [阶段一：Demo 生成提示词](#三阶段一demo-生成提示词)
4. [阶段二：领导审阅后迭代提示词](#四阶段二领导审阅后迭代提示词)
5. [Git 分支管理规范](#五git-分支管理规范)
6. [多用户协作规范](#六多用户协作规范)
7. [容器化时机建议](#七容器化时机建议)
8. [完整工作流串联](#八完整工作流串联)

---

## 一、提示词设计总体思路

### 核心原则

```
① 分阶段拆解  ——  Demo 阶段只做框架与原型，不追求生产质量
② 上下文延续  ——  每次调用 Agent 都携带完整项目状态与历史决策
③ 可验证输出  ——  每个 Agent 任务必须有明确的「完成标准」
④ Git 原子性  ——  每个功能点一个 commit，每个阶段一个 PR
⑤ 人工审查节点  ——  领导审阅是强制暂停点，Agent 不得自动跳过
```

### 提示词层级结构

```
┌─────────────────────────────────────────┐
│  L0：系统角色定义（每次调用都携带）        │
│  → 告诉 Agent 它是谁、项目背景是什么      │
├─────────────────────────────────────────┤
│  L1：阶段上下文（每个阶段开始时注入）      │
│  → 当前处于哪个阶段，约束条件是什么       │
├─────────────────────────────────────────┤
│  L2：任务提示词（每个具体模块任务）        │
│  → 做什么、怎么做、产出什么               │
├─────────────────────────────────────────┤
│  L3：约束提示词（质量与规范检查）          │
│  → 代码规范、Git 规范、输出格式要求        │
└─────────────────────────────────────────┘
```

---

## 二、主提示词（Master Prompt）

> **使用方式：** 每次启动新的 Agent 会话时，将此提示词作为 System Prompt 注入。

---

```
# 系统角色定义

你是一位资深全栈工程师 + 技术架构师，正在主导开发一套
「数字孪生洪水预报预警 + Agentic 智能平台」。

## 项目技术栈
- 前端：Vue 3 + Vite + TypeScript + Element Plus + ECharts + Cesium.js
- 后端：Spring Boot 3.x + Spring Cloud（Nacos + Gateway + OpenFeign）
- AI/优化：Python FastAPI + PyTorch + pymoo（NSGA-III）
- 数据层：Kafka + Flink + InfluxDB + PostgreSQL/PostGIS + Redis + MinIO
- 运维：Docker（开发期）→ Kubernetes（生产期，后置）

## 项目模块清单
- M01：数据大屏（监控驾驶舱）
- M02：实时详细数据页
- M03：后台管理系统
- M04：数据接入与预处理管道（Kafka + Flink）
- M05：预警引擎服务
- M06：多目标优化服务（NSGA-III + DRL）
- M07：AI 洪水预报服务（LSTM/Transformer）
- M08：数字孪生三维场景（Cesium.js）
- M09：Agentic 智能体编排服务
- M10：用户权限与认证服务（RBAC + JWT）
- M11：通知推送服务（WebSocket + 多渠道）

## 当前开发阶段
[由 L1 阶段上下文覆盖此字段]

## 行为准则
1. 每完成一个功能单元，必须提供对应的 Git commit 命令
2. 所有代码必须附带简短注释说明关键逻辑
3. Demo 阶段优先跑通流程，使用 Mock 数据，不写复杂业务逻辑
4. 每个模块完成后输出「模块自检清单」供人工验证
5. 遇到技术选型分歧时，提供 2-3 个方案对比，不自行决定
6. 代码文件路径必须符合项目目录规范（见下方规范）

## 项目目录规范
flood-platform/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── views/               # 页面级组件
│   │   ├── components/          # 通用组件
│   │   ├── stores/              # Pinia 状态
│   │   ├── api/                 # 接口封装
│   │   └── utils/               # 工具函数
├── backend/
│   ├── gateway-service/         # API 网关
│   ├── auth-service/            # 认证授权
│   ├── data-ingest-service/     # 数据接入
│   ├── alert-engine-service/    # 预警引擎
│   ├── optimization-service/    # 多目标优化编排
│   ├── admin-service/           # 后台管理
│   └── notify-service/          # 通知推送
├── python-services/
│   ├── ml-forecast-api/         # 预报模型
│   └── optimization-api/        # 优化计算
└── docs/                        # 文档
    ├── api/                     # API 文档
    ├── review/                  # 审阅记录
    └── changelog/               # 变更日志
```

---

## 三、阶段一：Demo 生成提示词

### 3.1 阶段启动提示词（注入 L1）

> **使用时机：** 开始 Demo 开发前，告知 Agent 当前所处阶段。

---

```
# 当前阶段：PHASE-1 Demo 原型开发

## 阶段目标
在 2 周内产出所有核心模块的可演示原型（Demo），
供领导进行第一次审阅，重点验证功能框架与交互逻辑。

## Demo 阶段约束（非常重要，严格遵守）
✅ 允许：
  - 使用 Mock 数据替代真实接口（mockjs / json-server）
  - 使用内存 Map 替代数据库操作
  - 组件样式粗糙，但布局结构必须完整
  - 业务逻辑简化（预警阈值写死、优化算法用随机解代替）

❌ 禁止：
  - 编写复杂的生产级错误处理
  - 接入真实传感器或外部 API（除非明确要求）
  - 过度设计（不写接口抽象层、不做性能优化）
  - 跳过 Git commit 步骤

## Demo 完成标准
每个模块必须满足：
  1. 页面/接口可正常运行，无控制台报错
  2. 核心交互流程可完整走通（点击→响应→数据展示）
  3. 已推送到对应的 feature 分支
  4. 已填写模块自检清单

## Git 分支规则（Demo 阶段）
基础分支：develop
每个模块创建：feature/demo-M[模块号]-[模块名]
合并方式：功能完成后提 PR → develop，由 Tech Lead 审核后合并
```

---

### 3.2 模块级任务提示词模板

> **使用方式：** 为每个模块单独调用，替换 `{{变量}}` 部分。

---

```
# 任务：生成 {{模块名称}} Demo

## 模块信息
- 模块编号：{{模块编号，如 M01}}
- 模块名称：{{如：数据大屏}}
- 负责人：{{开发者姓名}}
- 预计工时：{{如：2天}}

## 本次任务范围（Demo 阶段仅做以下部分）
{{逐条列出本次要实现的功能点，例如：
  1. 页面整体布局框架（三栏：左侧站点树、中间地图、右侧数据面板）
  2. ECharts 水位趋势图（使用 Mock 数据，展示过去 24h）
  3. 预警等级颜色标记（蓝/黄/橙/红，写死示例数据）
  4. 顶部关键指标卡（水位/雨量/流量，Mock 数值）
}}

## 技术要求
- 前端：Vue 3 <script setup> 语法，TypeScript，Element Plus 组件
- 数据：使用 mockjs 生成随机数据，数据结构需符合真实接口规范
- 样式：使用 Tailwind CSS 或 Element Plus 内置主题，暗色风格

## 输出要求（必须全部提供）
1. 完整可运行的代码文件（含文件路径）
2. Mock 数据结构说明（字段名、类型、示例值）
3. 组件树结构图（文字描述即可）
4. Git 操作命令序列（创建分支 → commit → push）
5. 模块自检清单（5-8条可勾选的验证项）
6. 遗留问题列表（Demo 中简化了哪些，后续需要补充什么）

## Git Commit 规范
格式：[类型](模块): 描述
类型：feat / fix / style / refactor / docs / test
示例：feat(M01-dashboard): add water level trend chart with mock data

## 注意事项
{{填写该模块的特殊注意点，例如：
  - Cesium 地图需要申请 token，Demo 阶段使用免费 Ion Token
  - 大屏需要支持 1920×1080 分辨率，使用 v-scale-screen
}}
```

---

### 3.3 各模块具体任务提示词（预填版）

#### M01 数据大屏

```
# 任务：生成 M01 数据大屏 Demo

## 本次任务范围
1. 全屏暗色大屏布局（顶部标题栏 + 左中右三栏）
2. 左栏：流域站点树形列表（Mock 3个流域，每个5个站点）
3. 中栏：Leaflet 二维地图（站点标记，点击显示弹窗）
4. 右栏上：ECharts 折线图（水位 24h 趋势，Mock 数据）
5. 右栏下：预警列表滚动（5条 Mock 预警，颜色分级）
6. 顶部：4个关键指标卡（当前水位/1h雨量/流量/预警数）
7. WebSocket 模拟（setInterval 每3秒更新一次数据，模拟推送）

## 技术要求
- v-scale-screen 实现 1920×1080 等比缩放
- ECharts 使用动态追加数据模拟实时效果
- 颜色方案：蓝色(正常) #1890FF / 黄色(注意) #FAAD14 /
            橙色(警告) #FA8C16 / 红色(紧急) #F5222D

## 输出要求（全部提供）
1. 完整代码（views/Dashboard.vue + components/下子组件）
2. Mock 数据结构
3. Git 操作命令
4. 自检清单
5. 遗留问题（Cesium 三维、真实 WebSocket 等后置项）
```

#### M02 实时详细数据页

```
# 任务：生成 M02 实时详细数据页 Demo

## 本次任务范围
1. 站点选择器（下拉框，Mock 10个站点）
2. 时间范围选择器（Element Plus DateTimePicker，预设：1h/6h/24h/7d）
3. 水位-雨量-流量 三联图（ECharts，共用 X 轴时间轴）
4. 数据明细表格（Element Plus Table，分页，每页20条）
5. 多目标优化结果展示区（帕累托前沿 Mock 散点图，5个方案点）
6. 导出按钮（弹窗提示「导出功能开发中」即可）

## 技术要求
- ECharts 三联图联动（鼠标悬停同步十字线）
- 帕累托散点图：X轴=防洪效益，Y轴=发电效益，颜色=推荐方案高亮
- 表格支持按水位/时间排序
```

#### M03 后台管理系统

```
# 任务：生成 M03 后台管理系统 Demo

## 本次任务范围
1. 整体布局（Element Plus Container：侧边栏 + 顶部导航 + 内容区）
2. 侧边栏菜单（站点管理/预警规则/用户管理/系统日志，图标+文字）
3. 站点管理页：CRUD 表格（Mock 10条站点，新增/编辑/删除弹窗）
4. 预警规则配置页：表单（阈值设定，4级 × 3项指标）
5. 用户管理页：表格+角色标签（超管/省级/市级，Mock 5个用户）
6. 系统日志页：只读表格（Mock 日志，支持关键字搜索）

## 技术要求
- 使用 Vue Router 嵌套路由
- CRUD 操作使用 Pinia Mock Store，刷新后数据重置（Demo 允许）
- 表单验证使用 Element Plus Form Validation
```

#### M04 数据接入与预处理（后端）

```
# 任务：生成 M04 数据接入与预处理管道 Demo

## 本次任务范围（后端 Spring Boot）
1. data-ingest-service：HTTP 接口接收 Mock 传感器数据（POST /api/sensor/data）
2. 简单数据校验（范围检验：水位 0~20m，雨量 0~500mm/h）
3. 发布到 Kafka Topic：flood.sensor.raw（Demo 可用内存队列 LinkedBlockingQueue 替代）
4. preprocess-service：消费队列，执行简单清洗（去除 null，超范围置为 null）
5. 写入 InfluxDB（Demo 可用 H2 内存数据库 + 时间戳字段模拟）
6. REST API：GET /api/sensor/latest?stationId=xxx 返回最新数据

## 输出要求
1. 两个 Spring Boot 服务的核心代码（Controller/Service/Model）
2. application.yml 配置（含 Mock 替代说明注释）
3. Postman 测试用例（JSON 格式）
4. Git 操作命令
5. 自检清单（用 curl 命令验证接口可用）
```

#### M05 预警引擎

```
# 任务：生成 M05 预警引擎服务 Demo

## 本次任务范围
1. 预警规则加载（从数据库/Mock 配置读取4级阈值）
2. 预警计算接口：POST /api/alert/evaluate（传入站点数据，返回预警等级）
3. 预警事件持久化（Mock：存内存 List，提供查询接口）
4. WebSocket 推送（STOMP，频道 /topic/alerts，每当新预警产生时推送）
5. 前端接收演示（在 M01 大屏中接入此 WebSocket，替换 setInterval Mock）

## 技术要求
- Spring WebSocket + STOMP 配置
- 预警等级枚举：BLUE(注意)/YELLOW(预警)/ORANGE(警告)/RED(紧急)
- 推送消息格式（JSON）：
  {stationId, stationName, level, metric, value, threshold, timestamp}
```

#### M06 多目标优化服务

```
# 任务：生成 M06 多目标优化服务 Demo

## 本次任务范围

### Python FastAPI 端（optimization-api）
1. POST /optimize/run  接收优化请求（水库参数 + 预见期）
2. Demo 用随机生成 20 个帕累托解代替真实 NSGA-III 计算
3. 每个解包含：{id, flood_benefit, power_benefit, water_supply_benefit,
               schedule: [{time, gate_opening, discharge}]}
4. 返回推荐解（综合得分最高）+ 完整解集

### Spring Boot 端（optimization-service）
1. POST /api/optimization/trigger  调用 Python 服务并缓存结果
2. GET  /api/optimization/result/{taskId}  查询结果
3. WebSocket 推送优化进度（0%→100% Mock 进度条）

### 前端（M02 详情页联动）
1. 触发优化按钮 + 进度条展示
2. 帕累托前沿散点图（ECharts scatter，可点击选择方案）
3. 选中方案后展示调度过程线（时间 vs 泄流量折线图）

## 输出要求
1. Python FastAPI 代码 + requirements.txt
2. Spring Boot 代码（含 WebClient 调用 Python 服务）
3. 前端组件代码
4. 接口联调说明（端口/路由/数据格式）
5. Git 操作命令（前后端分别）
```

#### M07 AI 预报服务（简化 Demo）

```
# 任务：生成 M07 AI 洪水预报服务 Demo

## 本次任务范围（Demo 极简版）
1. Python FastAPI：POST /forecast/run
   - 输入：过去 24h 的水位/雨量序列（JSON）
   - Demo：不加载真实模型，用简单线性趋势外推模拟预报
   - 输出：未来 24h/48h/72h 预报值 + 上下置信边界（±10% Mock）
2. Spring Boot forecast-service 调用代理
3. 前端：在 M02 详情页追加「预报曲线」（虚线 + 置信区间填充）

## 重要说明给领导审阅
在 Demo 注释中明确标注：
  // [DEMO-ONLY] 此处使用线性外推模拟，
  // 生产版本将替换为 LSTM/Transformer 模型
  // 预计在 Phase-4 完成真实模型集成
```

#### M10 用户认证与权限

```
# 任务：生成 M10 用户认证与权限服务 Demo

## 本次任务范围
1. auth-service：POST /auth/login（用户名+密码 → JWT Token）
2. Mock 用户表（5个内置账号，覆盖5种角色）：
   admin/admin123（超管）、province/p123（省级）、
   city/c123（市级）、county/co123（县级）、viewer/v123（观察员）
3. JWT 校验过滤器（Spring Security）
4. 前端登录页（Element Plus Form）
5. 路由守卫（未登录跳转登录页，角色权限控制菜单显示）
6. 前端权限指令（v-permission="['admin','province']"）

## 输出要求
- 内置账号清单（文档形式，方便演示时切换角色）
- 不同角色登录后菜单差异截图描述
```

---

## 四、阶段二：领导审阅后迭代提示词

### 4.1 审阅反馈收集模板

> **使用方式：** 领导审阅 Demo 后，将反馈整理成此格式，作为 Agent 下一轮输入。

---

```markdown
# 领导审阅反馈记录
审阅时间：{{YYYY-MM-DD}}
审阅人：{{姓名/职位}}
Demo 版本：v0.1.0-demo（tag: demo-review-v1）

## 反馈分类

### A. 必须修改（阻断性问题）
- [ ] {{问题1，如：大屏地图默认中心点不对，应聚焦到XX流域}}
- [ ] {{问题2，如：预警颜色与现行业务标准不符，需按照GB/T规范调整}}

### B. 建议优化（重要但不阻断）
- [ ] {{建议1，如：数据大屏左侧站点列表希望加上搜索过滤功能}}
- [ ] {{建议2，如：帕累托图希望能显示方案的文字说明}}

### C. 新增需求（原范围外）
- [ ] {{新需求1，如：需要增加一个「当日降雨累计」统计卡片}}
- [ ] {{新需求2，如：后台管理要能批量导入站点（Excel 上传）}}

### D. 确认保留（无需改动）
- {{功能点1}}
- {{功能点2}}

## 下一轮迭代优先级
P0（本周完成）：A 类全部
P1（下周完成）：B 类中标注「重要」的
P2（排期迭代）：C 类新需求，需评估工时后排期
```

---

### 4.2 迭代开发提示词（L1 替换）

---

```
# 当前阶段：PHASE-2 迭代优化（基于 Demo 审阅反馈）

## 背景
Demo v0.1.0 已完成领导审阅，审阅反馈已记录于 docs/review/review-v1.md。
当前任务是基于审阅反馈进行迭代开发。

## 迭代约束
✅ 本阶段允许：
  - 逐步替换 Mock 数据为真实接口（按模块优先级）
  - 引入真实 Kafka 连接（本地 Docker 启动即可）
  - 完善错误处理与表单验证
  - 针对审阅反馈进行 UI/UX 改进

❌ 本阶段仍暂缓：
  - Kubernetes 生产部署（容器化 Docker Compose 即可）
  - 真实 ML 模型训练与集成（仍用简化模型）
  - 性能压测与优化

## Git 工作流（迭代阶段）
- 基础分支切换为：main（develop 合并后已创建 release/v0.2.0）
- 每条审阅反馈对应一个 fix 或 feat 分支：
  fix/review-v1-{issue编号}-{简述}
  feat/review-v1-{需求编号}-{简述}
- 示例：
  fix/review-v1-A01-map-center-point
  feat/review-v1-C01-excel-station-import

## 本次迭代任务
[将 4.1 中整理的反馈逐条填入，Agent 按优先级逐个处理]
```

---

### 4.3 迭代任务提示词模板

---

```
# 迭代任务：处理审阅反馈 {{反馈编号}}

## 问题描述
{{从审阅反馈记录中粘贴原文}}

## 影响模块
{{如：M01-数据大屏 / views/Dashboard.vue}}

## 期望结果
{{描述修改后应该是什么效果}}

## 技术方案（如有明确思路）
{{可选：填写实现思路，或留空让 Agent 给出方案建议}}

## 约束
- 修改范围：尽量最小化改动，避免引入新问题
- 不得修改：{{列出不能动的文件/接口}}
- 需要同步修改：{{如：修改了数据结构需同步更新 Mock 和真实接口}}

## 输出要求
1. 修改后的完整代码（diff 格式或完整文件）
2. 修改说明（改了什么，为什么这样改）
3. Git 操作命令：
   git checkout -b fix/review-v1-{{编号}}-{{简述}}
   git add .
   git commit -m "fix({{模块}}): {{描述}}"
   git push origin fix/review-v1-{{编号}}-{{简述}}
4. 回归测试要点（改了这里，需要验证哪些功能没有被破坏）
```

---

## 五、Git 分支管理规范

### 5.1 分支结构总览

```
main                    # 生产分支（仅接受来自 release/* 的 PR）
│
├── develop             # 集成分支（所有 feature 汇聚于此）
│   │
│   ├── feature/demo-M01-dashboard          # Demo 阶段：大屏模块
│   ├── feature/demo-M02-detail-page        # Demo 阶段：详情页
│   ├── feature/demo-M03-admin              # Demo 阶段：后台管理
│   ├── feature/demo-M04-data-pipeline      # Demo 阶段：数据管道
│   ├── feature/demo-M05-alert-engine       # Demo 阶段：预警引擎
│   ├── feature/demo-M06-optimization       # Demo 阶段：多目标优化
│   ├── feature/demo-M07-forecast           # Demo 阶段：AI 预报
│   ├── feature/demo-M08-digital-twin       # Demo 阶段：数字孪生
│   ├── feature/demo-M09-agent              # Demo 阶段：Agentic
│   ├── feature/demo-M10-auth               # Demo 阶段：认证权限
│   └── feature/demo-M11-notify             # Demo 阶段：通知推送
│
├── release/v0.1.0-demo                     # Demo 审阅版本（打 tag）
├── release/v0.2.0                          # 迭代第一版
│   ├── fix/review-v1-A01-map-center
│   ├── fix/review-v1-A02-alert-color
│   └── feat/review-v1-C01-excel-import
│
└── hotfix/xxx                              # 紧急修复（仅生产出现问题时使用）
```

### 5.2 分支操作规范（Agent 必须遵守）

**① Demo 阶段 - 开始新模块**

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/demo-M01-dashboard

# 开发完成后
git add .
git commit -m "feat(M01): initial dashboard layout with mock data"
git push origin feature/demo-M01-dashboard

# 在 GitLab/GitHub 上创建 PR：feature/demo-M01-dashboard → develop
# PR 描述模板见 5.4
```

**② Demo 完成 - 打版本 Tag**

```bash
# develop 所有模块合并完成后
git checkout develop
git pull origin develop
git tag -a v0.1.0-demo -m "Demo v0.1.0 - 完整 Demo 原型，领导审阅版本"
git push origin v0.1.0-demo

# 从 develop 创建 release 分支（审阅期间开发继续在 develop 推进）
git checkout -b release/v0.1.0-demo
git push origin release/v0.1.0-demo
```

**③ 迭代阶段 - 处理审阅反馈**

```bash
# 从 develop 创建修复分支（不是从 release！）
git checkout develop
git pull origin develop
git checkout -b fix/review-v1-A01-map-center

# 修复完成
git add .
git commit -m "fix(M01-dashboard): correct map center to target watershed coordinates"
git push origin fix/review-v1-A01-map-center

# PR：fix/review-v1-A01-map-center → develop
```

### 5.3 Commit Message 规范

```
格式：[类型](作用域): 简短描述（中英文均可）

类型：
  feat     - 新功能
  fix      - 修复 Bug（含审阅反馈修改）
  style    - 样式调整（不影响逻辑）
  refactor - 重构（功能不变，代码结构改变）
  docs     - 文档更新
  test     - 测试相关
  chore    - 构建/依赖/配置变更
  mock     - Mock 数据变更（Demo 阶段专用）
  review   - 针对审阅反馈的修改（迭代阶段专用）

作用域（对应模块编号）：
  M01-dashboard / M02-detail / M03-admin / M04-pipeline /
  M05-alert / M06-optimization / M07-forecast / M08-twin /
  M09-agent / M10-auth / M11-notify

示例：
  feat(M01-dashboard): add realtime water level chart with mock websocket
  fix(M05-alert): correct alert threshold unit from mm to mm/h
  review(M01-dashboard): adjust map center point to Yangtze River basin
  docs(M06-optimization): add Pareto front interaction guide
```

### 5.4 PR（Pull Request）描述模板

```markdown
## 概述
[简述本 PR 做了什么]

## 模块
- 模块编号：M0X
- 相关文件：[列出主要改动文件]

## 变更类型
- [ ] 新功能（feat）
- [ ] Bug 修复（fix）
- [ ] 审阅反馈处理（review）
- [ ] 重构（refactor）

## Demo 阶段 Mock 说明（如适用）
[列出哪些地方用了 Mock，以及 TODO 后续替换计划]

## 自检清单
- [ ] 代码可正常运行，无控制台 Error
- [ ] 核心交互流程可完整走通
- [ ] 已添加必要注释
- [ ] Commit Message 符合规范
- [ ] 不影响其他已完成模块

## 截图/演示
[附上关键页面截图或录屏链接]

## 遗留问题
[列出 Demo 阶段刻意简化的部分，等待后续迭代]
```

---

## 六、多用户协作规范

### 6.1 团队角色与权限划分

| 角色 | 典型职责 | 分支权限 | 代码审查 |
|------|---------|---------|---------|
| **Tech Lead**（技术负责人） | 架构决策、PR 最终审核、main 分支管理 | 全部分支 push + merge | 审核所有 PR |
| **前端开发 A** | M01/M02/M08 模块 | feature/fix/* push，无 main/release push 权限 | 互相 Review 前端 PR |
| **前端开发 B** | M03/M10（前端部分）模块 | 同上 | 同上 |
| **后端开发 A** | M04/M05/M11 服务 | feature/fix/* push | 互相 Review 后端 PR |
| **后端开发 B** | M06/M07/M09 服务 + Python | 同上 | 同上 |
| **测试工程师** | 测试用例编写、Bug 提交 | 只读 + hotfix PR 提交权限 | 验收 PR |

### 6.2 日常协作工作流

```
每日节奏：
  09:00  站会（同步进度，暴露阻塞）
  随时   遇到接口联调问题 → 发到 #dev-api 频道，不私聊
  17:00  当日 PR 提交截止
  17:30  Tech Lead 完成 PR Review

每周节奏：
  周一   Sprint 计划（确认本周各人任务，更新 Jira/飞书 看板）
  周五   Demo 演示 + 周报（同步整体进度给领导）
```

### 6.3 接口联调协作规范

> **核心原则：** 前后端并行开发，接口契约先行

```bash
# Step 1：后端先定义接口契约（OpenAPI/Swagger）
# 在 docs/api/M0X-接口契约.yaml 中用 YAML 描述接口
# 提交到 develop，前端立即可以开始 Mock

# Step 2：前端基于契约文档生成 Mock
# 使用 json-server 或 mockjs 按接口格式 Mock

# Step 3：后端完成真实实现后，前端切换到真实接口
# 修改 .env.development 中的 VITE_API_BASE_URL 即可

# 接口变更必须：
# 1. 先在 docs/api/ 中更新契约文档
# 2. 在飞书/钉钉 #dev-api 频道 @相关人员
# 3. 给出至少 1 天缓冲期才能上线
```

### 6.4 冲突解决规范

```bash
# 拉取最新 develop，变基自己的分支（保持提交历史整洁）
git checkout feature/demo-M01-dashboard
git fetch origin
git rebase origin/develop

# 解决冲突后
git add .
git rebase --continue
git push origin feature/demo-M01-dashboard --force-with-lease
# 注意：只能用 --force-with-lease，不能用 --force
```

### 6.5 环境隔离规范

```
本地开发环境（每人独立）：
  .env.development → VITE_API_BASE_URL=http://localhost:8080
  Spring Boot → application-dev.yml（本地 H2/Mock 配置）

联调集成环境（共享，develop 分支自动部署）：
  http://dev.flood-platform.internal
  数据库独立（dev schema）
  每日凌晨重置 Mock 数据

Demo 演示环境（领导审阅用，release 分支手动部署）：
  http://demo.flood-platform.internal
  数据预置（固定的演示数据集，不受日常开发影响）
  审阅期间代码冻结，只允许 hotfix
```

---

## 七、容器化时机建议

### 结论：**容器化分两步走，不是最后做**

```
❌ 错误做法：所有代码写完了再容器化（代价极高，环境差异问题大量涌现）
✅ 正确做法：Docker 贯穿始终，Kubernetes 最后做
```

### 推荐时间线

```
阶段一（第1-2月）：基础中间件容器化
  ▶ 用 Docker Compose 启动：Kafka / InfluxDB / PostgreSQL / Redis / Nacos
  ▶ 应用服务本地直接运行（mvn spring-boot:run / vite dev）
  ▶ 目的：统一团队中间件版本，消除「我本地可以」问题

阶段二（第3-4月）：应用服务 Dockerfile
  ▶ 每个 Spring Boot 服务 + Python 服务添加 Dockerfile
  ▶ docker-compose.yml 增加应用服务定义
  ▶ 可选：用 docker compose up 一键启动全套服务（演示方便）
  ▶ 目的：为 CI/CD 打基础，Demo 演示时一键拉起

阶段三（第5-7月）：CI/CD 自动构建镜像
  ▶ GitLab CI / Jenkins 自动 build + push 到镜像仓库
  ▶ develop 分支推送 → 自动部署到 dev 环境
  ▶ release 分支 → 手动触发部署到 demo 环境

阶段五（第11-12月）：Kubernetes 生产部署
  ▶ 编写 Helm Chart
  ▶ 配置 HPA（水平自动扩缩容）
  ▶ 配置 PersistentVolume（数据库持久化）
  ▶ 多副本高可用验证
```

### 各阶段 Docker 配置参考

**阶段一：中间件 docker-compose.yml**

```yaml
# docker-compose.middleware.yml
# 使用方式：docker compose -f docker-compose.middleware.yml up -d

version: '3.8'
services:
  kafka:
    image: bitnami/kafka:3.6
    ports: ["9092:9092"]
    environment:
      KAFKA_CFG_NODE_ID: 0
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  influxdb:
    image: influxdb:2.7
    ports: ["8086:8086"]
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_ORG: flood-platform
      DOCKER_INFLUXDB_INIT_BUCKET: sensor-data
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: dev-token-123

  postgres:
    image: postgis/postgis:15-3.3
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: flood_platform
      POSTGRES_USER: flood_user
      POSTGRES_PASSWORD: flood_pass_dev

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  nacos:
    image: nacos/nacos-server:v2.3.0
    ports: ["8848:8848"]
    environment:
      MODE: standalone
```

**阶段二：应用服务 Dockerfile 模板**

```dockerfile
# backend/alert-engine-service/Dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```dockerfile
# python-services/optimization-api/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 八、完整工作流串联

```
                    ┌─────────────────────────────────┐
                    │       项目启动                    │
                    │  初始化仓库 + 分支结构             │
                    │  Docker Compose 中间件启动         │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       PHASE-1: Demo 开发          │
                    │  11个模块并行开发（feature/* 分支）│
                    │  每个模块：代码→自检→PR→Review     │
                    │  → develop 合并                   │
                    └──────────────┬──────────────────┘
                                   │ develop 稳定
                    ┌──────────────▼──────────────────┐
                    │       Demo 审阅准备               │
                    │  打 tag v0.1.0-demo               │
                    │  部署到 demo 环境                  │
                    │  准备演示脚本（10min 演示路径）     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       领导审阅（强制暂停点）        │
                    │  收集反馈 → 填写 review-v1.md     │
                    │  Tech Lead 分类优先级（P0/P1/P2） │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       PHASE-2: 迭代优化           │
                    │  P0 反馈：fix/* 分支，本周完成     │
                    │  P1 反馈：feat/* 分支，下周完成    │
                    │  P2 需求：排期评估，进入 backlog   │
                    │  逐步替换 Mock → 真实接口          │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       release/v0.2.0             │
                    │  集成测试 → 第二次审阅             │
                    │  ……（循环迭代）                   │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       PHASE-4: AI 集成            │
                    │  真实 ML 模型替换 Demo 模型        │
                    │  完整 Agentic 流程联调             │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       PHASE-5: 生产就绪           │
                    │  Kubernetes 部署                  │
                    │  性能压测 + 安全加固               │
                    │  交付验收                         │
                    └─────────────────────────────────┘
```

---

## 快速参考卡片

### Agent 调用速查

| 场景 | 使用哪个提示词 |
|------|-------------|
| 启动新会话 | 第二章「主提示词」作为 System Prompt |
| 开始 Demo 阶段 | 主提示词 + 3.1「阶段启动提示词」 |
| 开发某个具体模块 | 主提示词 + 3.1 + 3.3 对应模块提示词 |
| 领导审阅完，开始迭代 | 主提示词 + 4.2「迭代开发提示词」 |
| 处理某条具体反馈 | 主提示词 + 4.2 + 4.3「迭代任务提示词」 |

### Git 命令速查

```bash
# 开始新模块
git checkout develop && git pull && git checkout -b feature/demo-M0X-xxx

# 提交代码
git add . && git commit -m "feat(M0X): xxx"

# 打 Demo 审阅 Tag
git tag -a v0.1.0-demo -m "Demo审阅版本" && git push origin v0.1.0-demo

# 处理审阅反馈
git checkout develop && git pull && git checkout -b fix/review-v1-AXX-xxx

# 变基更新
git fetch origin && git rebase origin/develop
```

---

*提示词文档 v1.0 · 适用阶段：Phase 1 Demo → Phase 2 迭代*
