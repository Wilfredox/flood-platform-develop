# 数字孪生洪水预报预警平台

> Digital Twin Flood Forecast & Warning Platform

基于 **数字孪生** 理念，融合实时监测、AI预报、多目标优化调度的综合防洪决策支持系统。

---

## 📐 项目架构

```
flood-platform/
├── frontend/               # Vue 3 + Vite + TypeScript 前端
├── backend/                # Spring Boot 3.x 微服务 (Java 17)
│   ├── data-ingest-service/    # M04 数据接入与预处理 (:8081)
│   ├── alert-engine-service/   # M05 告警引擎         (:8082)
│   ├── auth-service/           # M10 认证授权         (:8083)
│   └── optimization-service/   # M06 优化调度代理     (:8084)
├── python-services/        # Python FastAPI 算法服务
│   ├── optimization-api/       # M06 NSGA-II 优化     (:9001)
│   └── ml-forecast-api/        # M07 ML 洪水预报      (:9002)
├── docker/                 # Docker Compose 中间件配置
└── docs/                   # 项目文档与管理文件
```

## 🛠 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + Composition API | 3.4+ |
| 构建工具 | Vite | 5.x |
| UI 组件 | Element Plus | 2.x |
| 图表 | ECharts | 5.x |
| 地图 | Leaflet.js + 天地图 API (Demo) → Cesium (Phase-4) | 1.9 |
| 状态管理 | Pinia | 2.x |
| 后端框架 | Spring Boot | 3.2.x |
| 算法服务 | FastAPI + Python | 3.11+ |
| 消息队列 | Kafka | 3.7 |
| 时序数据库 | InfluxDB | 2.7 |
| 关系数据库 | PostgreSQL | 16 |
| 缓存 | Redis | 7.x |
| 服务注册 | Nacos | 2.3 |

## 🚀 快速启动 (Demo 模式)

### 前端 (纯前端 Mock 模式，无需后端)

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

**Demo 账号:**

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |
| province | p123 | 省级用户 |
| city | c123 | 市级用户 |
| county | co123 | 县级用户 |
| viewer | v123 | 只读用户 |

### 后端微服务 (可选)

```bash
# 每个服务独立启动
cd backend/data-ingest-service
mvn spring-boot:run

cd backend/alert-engine-service
mvn spring-boot:run

cd backend/auth-service
mvn spring-boot:run

cd backend/optimization-service
mvn spring-boot:run
```

### Python 算法服务 (可选)

```bash
cd python-services/optimization-api
pip install -r requirements.txt
python main.py   # :9001

cd python-services/ml-forecast-api
pip install -r requirements.txt
python main.py   # :9002
```

### 中间件 (Phase-2+)

```bash
cd docker
docker-compose -f docker-compose.middleware.yml up -d
```

## 📊 功能模块

| 编号 | 模块 | 状态 | 说明 |
|------|------|------|------|
| M01 | 数据监控大屏 | ✅ Demo | 地图 + 水位图 + 告警列表 + 统计卡片 + 智能体 |
| M02 | 站点详情页 | ✅ Demo | 三联图 + Pareto + 调度时序 + 数据表 |
| M03 | 系统管理 | ✅ Demo | 站点/告警/用户/日志管理 |
| M04 | 数据接入 | 🔶 Stub | Spring Boot REST 接口桩 |
| M05 | 告警引擎 | 🔶 Stub | 四级阈值判定桩 |
| M06 | 优化调度 | 🔶 Stub | NSGA-II Mock Pareto |
| M07 | ML 预报 | 🔶 Stub | 线性外推模拟 |
| M09 | 智能体助手 | ✅ Demo | 嵌入大屏对话面板，四类智能体 Mock |
| M10 | 登录认证 | ✅ Demo | Mock JWT + 角色权限 |

## 🎨 设计规范

- **分辨率**: 1920 × 1080 (16:9)
- **主题**: 深色科技风
- **主色调**: `#0d1b2a` → `#1b2838` → `#2c3e50`
- **强调色**: `#409EFF` (Element Plus 蓝)
- **告警色**: 蓝 `#1890FF` / 黄 `#FAAD14` / 橙 `#FA8C16` / 红 `#F5222D`
- **字体**: `"HarmonyOS Sans SC", "PingFang SC", sans-serif`

## 📁 文档目录

- [提示词系统文档](docs/flood_platform_prompt_system.md)
- [项目路线图](docs/flood_platform_roadmap.md)
- [Git 分支策略](docs/project-management/git-branch-strategy.md)
- [技能矩阵](docs/project-management/skill-matrix.md)
- [风格指南](docs/project-management/style-guide.md)
- [开发日志](docs/project-management/dev-log.md)
- [待办清单](docs/project-management/todo-list.md)

## 📋 开发阶段

| 阶段 | 目标 | 周期 |
|------|------|------|
| **Demo** | 前端全功能演示 + 后端接口桩 | ← 当前 |
| Phase-2 | Kafka + InfluxDB 真实数据流 | 计划中 |
| Phase-3 | LSTM/Transformer 预报模型 | 计划中 |
| Phase-4 | Cesium 三维数字孪生 | 计划中 |
| Phase-5 | 性能优化 + 安全加固 | 计划中 |

---

> 📌 本项目为毕业设计/学术研究项目，所有数据均为模拟数据。
