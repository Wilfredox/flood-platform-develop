# 数字孪生洪水预报预警 + Agentic 智能平台
## 技术架构路线图 · 功能模块规划 · 实施方案

> **技术栈：** Vue 3 + Spring Boot + Spring Cloud · Kafka + Flink · InfluxDB + PostgreSQL · Docker + Kubernetes

---

## 目录

1. [平台定位与整体概述](#一平台定位与整体概述)
2. [技术选型确认与补充建议](#二技术选型确认与补充建议)
3. [系统整体架构分层设计](#三系统整体架构分层设计)
4. [实时数据池与数据预处理](#四实时数据池与数据预处理)
5. [功能模块详细规划](#五功能模块详细规划)
6. [多目标优化模块](#六多目标优化模块重点)
7. [Agentic 智能体模块](#七agentic-智能体模块)
8. [后端微服务拆分](#八后端微服务拆分)
9. [完整技术栈清单](#九完整技术栈清单)
10. [实施路线图](#十实施路线图五阶段)
11. [非功能性要求](#十一非功能性要求)
12. [可扩展增值模块](#十二可扩展增值模块)

---

## 一、平台定位与整体概述

本平台是一套面向流域防汛管理的**数字孪生 + AI 驱动（Agentic）综合智慧水利系统**，核心目标是通过实时数据采集、水文模型驱动、多目标优化与 AI 辅助决策，实现对洪水的精准预报、及时预警与科学调度。

### 平台三大核心能力

| 能力域 | 核心内容 |
|--------|---------|
| **感知 & 建模** | 多源实时传感接入、数字孪生流域仿真、水文水动力模型耦合、历史情景回溯 |
| **预报 & 预警** | AI 洪水预报（LSTM/Transformer）、多阈值分级预警、集合概率预报 |
| **决策 & 调度** | 多目标优化调度、Agentic 智能体协同、多部门应急指挥联动 |

---

## 二、技术选型确认与补充建议

### ✅ 确认采用（完全正确）

- **前端：** Vue 3 + Vite + TypeScript — 生态成熟，适合大屏与后台双场景
- **后端：** Spring Boot 3.x + Spring Cloud — 微服务首选，模块化拆分清晰
- **双向通信：** WebSocket（STOMP over SockJS）— Spring 生态标准方案
- **容器化：** Docker + Docker Compose（开发）/ Kubernetes（生产）

### ⚠️ 补充建议与纠正

| 问题点 | 原始说法 | 建议调整 |
|--------|---------|---------|
| 数据池 | 模糊的「数据池」概念 | 明确为 **Kafka + Flink + InfluxDB** 三层管道架构 |
| AI 推理 | 放在 Spring Boot 里 | 独立为 **Python FastAPI 微服务**，Spring Boot 调用即可 |
| 三维渲染 | 未提及 | 引入 **Cesium.js**（地理 GIS）做数字孪生三维场景 |
| 多目标优化 | 未提及 | 需独立设计优化服务，建议 **NSGA-III / MOEA/D** 算法 |

---

## 三、系统整体架构分层设计

系统采用**六层架构**，每层职责清晰、接口标准，支持独立部署与水平扩展。

```
┌─────────────────────────────────────────────────────────────┐
│  ⑥ 运维层   Docker · Kubernetes · Jenkins · Prometheus · ELK │
├─────────────────────────────────────────────────────────────┤
│  ⑤ 应用层   数据大屏 · 实时详情 · 后台管理 · 数字孪生三维      │
│             Vue 3 + Cesium.js + ECharts + Element Plus        │
├─────────────────────────────────────────────────────────────┤
│  ④ 通信层   REST API · WebSocket 双向推送 · 消息总线           │
│             Spring Cloud Gateway + STOMP/WebSocket            │
├─────────────────────────────────────────────────────────────┤
│  ③ 服务层   数据接入 · 预处理 · 预警引擎 · 多目标优化           │
│             Spring Boot 微服务 + Python FastAPI（ML/优化）     │
├─────────────────────────────────────────────────────────────┤
│  ② 数据层   Kafka · Flink · InfluxDB · PostgreSQL · Redis     │
│             MinIO · Elasticsearch                             │
├─────────────────────────────────────────────────────────────┤
│  ① 感知层   水位站 · 雨量站 · 气象雷达 · 卫星遥感 · 无人机     │
│             MQTT / Modbus / HTTP 边缘网关                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、实时数据池与数据预处理

> 您提到的「数据池」建议升级为工程级的**三层数据管道**架构。

### 4.1 三层数据管道

```
传感器设备
    │  MQTT / HTTP / Modbus
    ▼
┌─────────────────────────────┐
│  第一层：数据采集与接入        │
│  EMQX（MQTT Broker）         │
│  协议适配器（Spring Boot）    │
│  → 标准化消息推入 Kafka Topic │
└────────────┬────────────────┘
             │ Kafka
             ▼
┌─────────────────────────────┐
│  第二层：实时流处理（Flink）   │
│  · 数据清洗（异常值/缺失值）   │
│  · 单位统一 & 时间戳对齐      │
│  · 滑动窗口聚合（5min/1h/6h）│
│  · 超阈值事件检测 → Alert     │
│  · ML 特征工程实时计算        │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  第三层：多模态数据存储（按查询特性分库）           │
│                                                  │
│  InfluxDB    → 高频时序指标（水位/流量/雨量）      │
│  PostgreSQL  → 业务数据 + PostGIS 空间查询        │
│  Redis       → 最新传感器快照、预警状态（毫秒级）   │
│  MinIO       → 遥感影像、无人机视频、雷达图         │
│  Elasticsearch → 日志、告警历史全文检索            │
└─────────────────────────────────────────────────┘
```

### 4.2 数据预处理核心算法

**数据质量控制**
- 范围检验：超出物理范围标记为无效值
- 时序一致性：突变值识别（差分检验）
- 空间一致性：相邻站点数据交叉验证
- 传感器故障检测：连续固定值 / 长时间无数据告警

**特征工程计算**
- 滑动均值 / 指数移动平均（EMA）
- 降雨强度等级计算（小雨 / 中雨 / 大雨 / 暴雨 / 大暴雨）
- 洪峰流量估算：流量过程线积分
- 超警戒线持续时间统计

**缺失值插补策略**
- 短时缺失（< 30min）：线性插值
- 中等缺失（30min ~ 2h）：样条插值
- 长时缺失（> 2h）：相邻站点回归估算 + 标记置信度

---

## 五、功能模块详细规划

### 5.1 前端功能模块（Vue 3）

#### 模块 A：数据大屏（监控驾驶舱）

| 功能项 | 技术实现 |
|--------|---------|
| 全局流域 GIS 地图 | Cesium.js（三维）/ Leaflet（二维），站点分布 + 淹没范围动态渲染 |
| 关键指标卡 | 实时水位、雨量、流量、预警等级（蓝/黄/橙/红四色编码） |
| 水位趋势图 | ECharts 动态折线图，24h/72h 历史 + 预报曲线（含置信区间） |
| 预警滚动列表 | WebSocket 实时推送，支持按流域/等级过滤 |
| 防汛资源地图 | 避险路线、应急物资仓库、抢险队伍实时 GPS 位置 |
| 视频监控矩阵 | 重点站点摄像头实时画面，6/9/16 宫格可切换 |
| 多目标优化结果展示 | 帕累托前沿可视化（散点图）、当前推荐调度方案高亮 |
| 全屏自适应 | v-scale-screen 等比缩放，支持 1920/2560/LED 大屏 |

#### 模块 B：实时详细数据页

- 单站点详情：历史曲线、数据列表（分页）、传感器健康状态
- 多站点对比图：同流域水位联动对比，可拖拽选择时间范围
- 降雨-径流分析：相关散点图、降雨空间分布热力图
- 洪水预报详情：24h/48h/72h 分级预报 + 不确定性可视化（扇形图）
- 多目标优化详情页：目标函数权重调节、帕累托解集浏览、方案对比表
- 数据导出：CSV / Excel 下载、图表截图（PNG/PDF）
- 历史回放：任意时段动态回放，支持变速（0.5x ~ 10x）

#### 模块 C：后台管理系统

- 站点管理：传感器注册/注销、参数配置、数据质量报告
- 预警规则配置：多级阈值设定、AND/OR 组合触发条件
- **优化模型配置**：目标函数权重管理、约束条件设定、算法参数调优
- 用户权限管理：RBAC（超管 / 省级 / 市级 / 县级 / 观察员）
- 通知渠道配置：短信（阿里云 SMS）、企微/钉钉 Webhook、Email、APP Push
- 调度预案管理：预案 CRUD、触发条件绑定、一键启动
- 系统日志审计：操作日志、接口调用、数据变更，全量不可删改
- 数据字典管理：流域编码、行政区划、设备类型等基础数据维护

---

## 六、多目标优化模块（重点）

> 洪水调度本质上是一个典型的多目标优化问题——防洪安全、发电效益、供水保障、生态流量等目标之间存在不可避免的冲突，需要在帕累托意义下寻求最优权衡方案。

### 6.1 优化问题建模

#### 目标函数（可配置）

```
目标 1：最大化防洪安全性
  → 最小化超警戒水位时长 / 最小化最高洪峰流量

目标 2：最大化发电效益
  → 在调度周期内最大化发电量（∑ N(t) · Δt）

目标 3：最大化供水保障率
  → 最小化下游供水缺口（∑ max(0, D(t) - Q(t))）

目标 4：满足生态基流要求
  → 最小化生态流量违约率（断流时段占比）

目标 5：最小化弃水损失
  → 最小化弃水量（溢洪道泄量超出需求部分）
```

#### 决策变量

- 水库群各时段闸门开度序列：`u(t) = [u₁(t), u₂(t), ..., uₙ(t)]`
- 泵站启停与功率调节序列
- 蓄水水位调控目标序列

#### 约束条件

```
硬约束（必须满足）：
  · 水库库容约束：Z_min ≤ Z(t) ≤ Z_max
  · 下泄流量约束：Q_min ≤ Q(t) ≤ Q_max（防止下游冲刷）
  · 水位变幅约束：|ΔZ(t)| ≤ ΔZ_max（防止坝坡失稳）
  · 发电机组约束：振动区回避、开机台数限制

软约束（允许微小违约，带惩罚项）：
  · 生态流量保障目标
  · 供水量日变化平稳性
```

### 6.2 算法选型

| 算法 | 适用场景 | 优势 |
|------|---------|------|
| **NSGA-III** | 3个以上目标、大规模水库群 | 参考点机制，多目标分布均匀 |
| **MOEA/D** | 目标函数可分解、实时性要求高 | 收敛速度快，适合在线优化 |
| **MOPSO** | 连续决策变量、快速响应 | 实现简单，易并行化 |
| **深度强化学习（MADDPG）** | 长序列决策、多智能体协同 | 自适应学习，离线训练在线推理 |
| **混合策略** | 生产推荐 | NSGA-III 离线 + DRL 在线微调 |

> **推荐方案：** 离线阶段用 NSGA-III 生成帕累托前沿并存入方案库；在线阶段用 DRL 智能体根据实时水情快速检索/微调最优解，兼顾全局最优与实时响应。

### 6.3 优化服务架构

```
前端（Vue 3）
  │  调整权重 / 触发优化请求
  ▼
Spring Boot（优化编排服务）
  │  任务调度 + 结果持久化
  ▼
Python FastAPI（优化计算服务）
  ├── NSGA-III / MOEA/D（pymoo 库）
  ├── 水文水动力仿真模型（HEC-RAS / SWMM 耦合）
  └── DRL 在线推理（PyTorch / Stable-Baselines3）
  │
  ▼
结果返回：帕累托解集 + 推荐方案 + 置信度评分
  │
  ▼
WebSocket 实时推送给前端 → 大屏展示帕累托前沿图
```

### 6.4 优化结果可视化

- **帕累托前沿图**：二维/三维散点图展示所有非劣解，交互式选择当前推荐方案
- **雷达图**：各目标归一化得分对比（防洪 / 发电 / 供水 / 生态）
- **调度过程线**：推荐方案下各水库水位、泄流量随时间变化曲线
- **方案对比表**：多个候选方案的关键指标横向对比，支持一键采纳
- **权重敏感性分析**：调节目标权重滑块，实时观察最优方案漂移

### 6.5 多目标优化与 Agentic 联动

```
实时水情预报结果
        │
        ▼
多目标优化引擎（生成帕累托前沿）
        │
        ▼
Agentic 决策智能体
  ├── 解读帕累托解集
  ├── 结合当前防汛形势（预警等级、社会影响）自动选择推荐方案
  ├── 生成自然语言调度说明（\"推荐方案：当前应以防洪为主，建议...\"）
  └── 推送至指挥长审批 → 一键下发执行
```

---

## 七、Agentic 智能体模块

### 7.1 总体架构：Router + 七大专业 Agent

系统采用 **一个路由 Agent + 七个专业 Agent** 的分层架构，由 LangGraph（Python）编排，LLM（DeepSeek API）驱动意图识别与自然语言交互，各 Agent 通过 Function Calling 调用后端模型服务。

```
┌────────────────────────────────────────────────────────────────────┐
│                      Router Agent（总调度）                         │
│              DeepSeek API · 意图识别 · 任务拆解 · 结果汇总          │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────────────────────┘
   │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼
 数据    新安江   LSTM   水力学  工程    融合   报告
 采集    水文    预测    演算   调度    研判   生成
 Agent   Agent  Agent  Agent  Agent  Agent  Agent
```

### 7.2 智能体能力矩阵

| # | 智能体 | 核心功能 | 调用的模型/服务 | 服务端口 |
|---|--------|---------|---------------|---------|
| 0 | **Router Agent** | 意图识别、任务拆解、多 Agent DAG 编排 | DeepSeek API (LLM) | — |
| 1 | **数据采集 Agent** | 拉取水雨情、河道断面、水库参数 | 数据库查询 + 外部 API 对接 | :8081 |
| 2 | **新安江水文 Agent** | 蓄满产流、三水源汇流计算 | 新安江模型 (NumPy 自研) | :9003 |
| 3 | **LSTM 预测 Agent** | 洪水过程预测、误差修正、预见期延伸 | LSTM/Transformer (PyTorch) | :9002 |
| 4 | **水力学 Agent** | 河道水位演算、流速计算、淹没范围分析 | 圣维南方程简化求解 / 曼宁公式 (NumPy) | :9004 |
| 5 | **工程调度 Agent** | 水库/闸门/泵站联合多目标优化调度 | NSGA-II / MOEA/D (Pymoo) | :9001 |
| 6 | **融合研判 Agent** | 多模型结果融合、态势综合评估 | 残差修正 / BMA / 规则引擎 | 内置 |
| 7 | **报告生成 Agent** | 汇总研判、生成文档、推送地图操控指令 | DeepSeek API (LLM) | — |

### 7.3 统一模型接口契约

所有后端模型服务遵循统一的 `TimeSeriesInput / TimeSeriesOutput` 数据契约，保证模型可插拔替换：

```python
# 统一输入
class TimeSeriesInput(BaseModel):
    station_id: str
    start_time: datetime
    end_time: datetime
    variables: dict[str, list[float]]  # {"rainfall": [...], "evaporation": [...]}
    dt: int = 3600  # 时间步长(秒)

# 统一输出
class TimeSeriesOutput(BaseModel):
    station_id: str
    timestamps: list[datetime]
    variables: dict[str, list[float]]  # {"discharge": [...], "water_level": [...]}
    metadata: dict  # 模型名称、置信区间、运行耗时等
```

每个模型服务只需实现 `POST /predict` 端点：

| 模型服务 | 端口 | 输入 | 输出 |
|---------|------|------|------|
| 新安江产汇流模型 | :9003 | 降雨 P(t)、蒸发 E(t) | 流量 Q(t) |
| LSTM 洪水预测 | :9002 | 历史流量序列 | 未来流量 Q(t+Δ) |
| 水力学演算 | :9004 | 上游流量边界 + 断面数据 | 沿程水位 Z(x,t)、淹没 GeoJSON |
| 多目标优化求解 | :9001 | 入库流量 + 约束条件 | 帕累托调度方案集 |

### 7.4 三种协作模式

#### 模式一：串行链（有严格依赖）

```
数据 Agent → 新安江 Agent → LSTM Agent → 报告 Agent
```

#### 模式二：并行竞争（同任务多模型并跑，结果融合）

```
              ┌→ [新安江 Agent] → Q_xaj(t) ─┐
数据 Agent ──┤                               ├→ [融合 Agent] → Q_fused(t)
              └→ [LSTM Agent]   → Q_lstm(t) ─┘
```

#### 模式三：串并混合 DAG（典型完整场景）

```
Data Agent
    │
    ├──→ 新安江 Agent ──┐
    │     (产汇流)       ├──→ Fusion Agent ──→ 工程调度 Agent ──→ 水力学 Agent
    └──→ LSTM Agent ───┘      (残差修正)       (NSGA-II)        (水位验证)
          并行                    汇聚              串行              串行
                                                     │
                                                     ▼
                                              Report Agent → Map Agent（推地图指令）
```

### 7.5 LangGraph DAG 编排示例

```python
from langgraph.graph import StateGraph, END

class FloodState(TypedDict):
    query: str                    # 用户原始输入
    rainfall: list[float]         # 降雨序列
    xaj_discharge: list[float]    # 新安江输出
    lstm_discharge: list[float]   # LSTM 输出
    fused_discharge: list[float]  # 融合结果
    schedule: dict                # 调度方案
    flood_map: dict               # 淹没分析 GeoJSON
    report: str                   # 最终报告

graph = StateGraph(FloodState)

graph.add_node("data_agent",     fetch_rainfall)
graph.add_node("xaj_agent",      run_xaj_model)
graph.add_node("lstm_agent",     run_lstm_model)
graph.add_node("fusion_agent",   fuse_results)
graph.add_node("schedule_agent", run_optimization)
graph.add_node("hydraulic_agent",run_hydraulic)
graph.add_node("report_agent",   generate_report)

graph.set_entry_point("data_agent")
graph.add_edge("data_agent",  "xaj_agent")       # 串行：先拿数据
graph.add_edge("data_agent",  "lstm_agent")       # 并行：同时跑两个模型
graph.add_edge("xaj_agent",   "fusion_agent")
graph.add_edge("lstm_agent",  "fusion_agent")     # 汇聚
graph.add_edge("fusion_agent", "schedule_agent")  # 串行
graph.add_edge("schedule_agent","hydraulic_agent") # 串行：验证方案
graph.add_edge("hydraulic_agent","report_agent")
graph.add_edge("report_agent", END)

app = graph.compile()
```

### 7.6 模型融合策略

新安江（物理机理）与 LSTM（数据驱动）并行输出后，由融合 Agent 结合：

| 策略 | 公式 / 做法 | 适用场景 |
|------|------------|---------|
| 简单加权 | $Q_{fused} = \alpha \cdot Q_{xaj} + (1-\alpha) \cdot Q_{lstm}$，$\alpha$ 按历史精度动态调整 | 快速上手 |
| **残差修正（推荐）** | $Q_{fused} = Q_{xaj} + \Delta Q_{lstm}$，LSTM 学习新安江的系统偏差 | 物理保底 + AI 修正 |
| 贝叶斯模型平均 (BMA) | 按后验概率分配权重 | 论文加分 |

### 7.7 自然语言 → 地图操控联动

将 Leaflet 地图操作封装为 LLM Function/Tool，通过 WebSocket 实现 Agent 操控前端地图：

```python
# Agent 可调用的地图工具示例
@tool
def draw_flood_zone(geojson: str, level: str):
    """在地图上绘制洪水淹没区域"""
    ws.send(json.dumps({"action": "draw_zone", "data": geojson, "level": level}))

@tool
def run_forecast(station_id: str, hours: int):
    """调用洪水预报模型"""
    return requests.post("http://ml-forecast-api:9002/predict", json={...}).json()
```

前端 WebSocket 监听 Agent 指令并执行地图渲染：

```js
ws.onmessage = (msg) => {
  const cmd = JSON.parse(msg.data)
  if (cmd.action === 'draw_zone')  map.addLayer(L.geoJSON(cmd.data))
  if (cmd.action === 'zoom_to')    map.flyTo(cmd.center, cmd.zoom)
  if (cmd.action === 'add_marker') L.marker(cmd.latlng).addTo(map)
}
```

### 7.8 LLM 技术路线

| 路线 | 方案 | 成本 | 推荐度 |
|------|------|------|--------|
| **API 调用（推荐）** | DeepSeek-V3 / 通义千问 | 极低（百万 token ≈ 1 元） | 开发快、Function Calling 成熟 |
| 本地部署 | Qwen2.5-7B / GLM-4-9B | 需 16GB+ 显存 GPU | 体现自主可控，部署成本高 |
| 混合方案 | API 为主 + 本地小模型做意图分类 | 折中 | 敏感数据走本地，通用推理走 API |

### 7.9 完整工作流示例

```
监管者（语音/文本）: "看看明天暴雨水库扛不扛得住"

Router Agent 拆解任务:
  1. Data Agent → 并行拉取: 气象降雨预报、水库参数、历史水文
  2. 新安江 Agent ∥ LSTM Agent → 并行计算入库流量
  3. Fusion Agent → 残差修正 → 最优流量预测
  4. 工程调度 Agent → NSGA-II → 3 套帕累托调度方案
  5. 水力学 Agent → 验证每套方案下游水位 + 淹没范围
  6. Map Agent → 淹没 GeoJSON 渲染到地图 + 调度过程动画
  7. Report Agent → "方案 B 最优：最大泄量 3200 m³/s，下游水位 37.8m，
                     低于警戒 0.2m，建议采纳..."

全程用户只说了一句话。
```

---

## 八、后端微服务拆分

```
spring-cloud-parent/
├── gateway-service          # API 网关（路由/限流/鉴权）
├── auth-service             # 用户认证授权（JWT + RBAC）
├── data-ingest-service      # 数据接入（MQTT/HTTP协议适配 + Kafka生产者）
├── preprocess-service       # 预处理管理（Flink Job 调度与监控）
├── alert-engine-service     # 预警引擎（规则计算 + 分级触发）
├── forecast-service         # 预报调用代理（调 Python FastAPI）
├── optimization-service     # 多目标优化编排（调 Python 优化服务）
├── twin-service             # 数字孪生（GIS数据/三维模型/淹没仿真）
├── agent-service            # Agentic 智能体编排（LangChain4j）
├── notify-service           # 通知推送（短信/企微/WebSocket）
├── file-service             # 文件管理（MinIO封装）
├── admin-service            # 后台管理（设备/规则/预案/字典）
└── monitor-service          # 系统监控（Prometheus 指标采集）

python-services/
├── ml-forecast-api          # 洪水预报模型（LSTM/Transformer）FastAPI  :9002
├── xaj-model-api            # 新安江水文模型（NumPy 自研）FastAPI       :9003
├── hydraulic-api            # 水力学演算（圣维南/曼宁）FastAPI          :9004
├── optimization-api         # 多目标优化服务（pymoo NSGA-II）FastAPI   :9001
└── agent-orchestrator       # LangGraph 多 Agent 编排 + DeepSeek LLM   :9010
```

### 服务间通信

| 通信场景 | 协议 | 说明 |
|---------|------|------|
| 同步业务调用 | REST（Spring Cloud OpenFeign）| 低延迟服务间调用 |
| 异步事件驱动 | Kafka | 数据流、预警事件、调度指令 |
| 实时推送前端 | WebSocket（STOMP） | 水情数据、预警、优化结果 |
| Spring → Python | HTTP REST / gRPC | 调用 ML 推理与优化计算 |
| 服务注册发现 | Nacos | 服务发现 + 配置中心 |

---

## 九、完整技术栈清单

### 前端

| 类别 | 技术 | 版本/说明 |
|------|------|---------|
| 框架 | Vue 3 + Vite + TypeScript | Composition API |
| UI 组件 | Element Plus | 后台管理系统 |
| 地图三维 | Cesium.js | 数字孪生 GIS |
| 二维地图 | Leaflet.js | 轻量化场景 |
| 图表 | Apache ECharts 5 | 标准数据可视化 |
| 定制图形 | D3.js | 帕累托前沿等高级图 |
| 大屏适配 | v-scale-screen | 等比缩放多分辨率 |
| 状态管理 | Pinia | 轻量 TS 友好 |
| HTTP | Axios | 统一请求拦截封装 |
| WebSocket | SockJS + STOMP.js | 双向实时通信 |

### 后端

| 类别 | 技术 | 说明 |
|------|------|------|
| 框架 | Spring Boot 3.x | 微服务基础 |
| 微服务 | Spring Cloud 2023 | 全家桶套件 |
| 网关 | Spring Cloud Gateway | 路由/限流/鉴权 |
| 服务注册 | Nacos | 服务发现 + 配置中心 |
| 熔断限流 | Sentinel | 服务保护 |
| 消息队列 | Apache Kafka | 高吞吐实时数据流 |
| 流处理 | Apache Flink | 有状态流计算 |
| 认证 | Spring Security + JWT | 无状态认证 |
| ORM | MyBatis-Plus | 关系型数据操作 |
| Agentic | LangChain4j | Java AI 应用框架 |

### AI / 优化 / 水文（Python 服务）

| 类别 | 技术 | 说明 |
|------|------|------|
| 服务框架 | FastAPI + Uvicorn | 高性能异步 API |
| 深度学习 | PyTorch | LSTM/Transformer 洪水预测 |
| 多目标优化 | pymoo | NSGA-II / NSGA-III / MOEA/D |
| 水文模型 | 新安江模型 (NumPy 自研) | 蓄满产流 + 三水源汇流 |
| 水力学模型 | 圣维南方程 / 曼宁公式 (NumPy) | 一维水位演算 + 淹没分析 |
| 智能体编排 | LangGraph + LangChain | 多 Agent DAG 编排 + Function Calling |
| LLM 接口 | DeepSeek API / 通义千问 | 意图识别 + 自然语言生成 |
| 强化学习 | Stable-Baselines3 | DRL 在线调度（可选） |
| 科学计算 | NumPy / SciPy / Pandas | 数据处理 |

### 数据存储

| 类别 | 技术 | 用途 |
|------|------|------|
| 时序数据库 | InfluxDB 2.x | 传感器高频时序指标 |
| 关系数据库 | PostgreSQL + PostGIS | 业务数据 + 空间查询 |
| 缓存 | Redis | 快照缓存、会话、分布式锁 |
| 搜索引擎 | Elasticsearch | 日志、告警全文检索 |
| 对象存储 | MinIO | 影像、视频、文件 |

### 基础设施

| 类别 | 技术 | 说明 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 开发/测试环境 |
| 容器编排 | Kubernetes + Helm | 生产环境弹性伸缩 |
| CI/CD | Jenkins / GitLab CI | 自动构建测试部署 |
| 监控 | Prometheus + Grafana | 指标采集与可视化 |
| 链路追踪 | SkyWalking | 微服务调用链分析 |
| 日志 | ELK Stack | 集中日志管理 |

---

## 十、实施路线图（五阶段）

```
第1-2月          第3-4月          第5-7月          第8-10月         第11-12月
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ 阶段一   │────▶│ 阶段二   │────▶│ 阶段三   │────▶│ 阶段四   │────▶│ 阶段五   │
│ 基础搭建 │     │ 数据管道 │     │ 核心功能 │     │ 智能增强 │     │ 生产就绪 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### 阶段一：基础架构搭建（第 1-2 月）

**目标：** 跑通整体架构骨架，不写业务代码

- [ ] Spring Cloud 微服务脚手架初始化（Nacos + Gateway + 基础服务）
- [ ] Docker Compose 本地开发环境（Kafka / InfluxDB / PostgreSQL / Redis）
- [ ] Vue 3 项目初始化（路由 / Pinia / Axios / ECharts / Cesium）
- [ ] CI/CD 流水线搭建（GitLab + Jenkins）
- [ ] 基础 RBAC 权限体系（Spring Security + JWT）
- [ ] 开发规范文档（API 设计规范 / Git 分支策略 / 代码审查流程）

**里程碑 M1：** 基础架构完成，模拟数据可在系统中流转

---

### 阶段二：数据管道建设（第 3-4 月）

**目标：** 实时数据从传感器流转到存储层，管道稳定可靠

- [ ] 边缘网关 + EMQX MQTT Broker 部署
- [ ] 多协议数据接入服务（MQTT / HTTP / FTP）
- [ ] Kafka Topic 设计与分区策略（按流域分区）
- [ ] Flink 数据清洗流作业（异常值/缺失值/单位统一）
- [ ] Flink 滑动窗口聚合作业（5min / 1h / 6h）
- [ ] InfluxDB 数据写入与 Flux 查询封装
- [ ] WebSocket 实时推送验证（传感器数据→前端大屏）
- [ ] 数据质量监控看板

**里程碑 M2：** 真实传感器数据接入，预处理管道运行稳定

---

### 阶段三：核心功能开发（第 5-7 月）

**目标：** MVP 可用系统，核心业务闭环

- [ ] 数据大屏开发（GIS 地图 + 关键指标 + ECharts 趋势图）
- [ ] 实时详情数据页（单站/多站对比/导出）
- [ ] 预警引擎开发（规则配置 + 分级触发 + 通知推送）
- [ ] 后台管理系统（站点/规则/用户/预案管理）
- [ ] 多目标优化基础版（NSGA-III + 防洪/发电/供水三目标）
- [ ] 优化结果可视化（帕累托前沿图 + 方案对比表）
- [ ] 历史数据回放功能

**里程碑 M3：** MVP 内测上线，核心功能可供用户试用

---

### 阶段四：AI 智能增强（第 8-10 月）

**目标：** AI 驱动的完整智慧平台

- [ ] LSTM / Transformer 洪水预测模型训练与 FastAPI 部署
- [ ] 新安江水文模型 Python 实现（蓄满产流 + 三水源汇流）
- [ ] 水力学简化模型（一维圣维南方程 / 曼宁公式 + 淹没 GeoJSON）
- [ ] 统一 TimeSeriesInput / TimeSeriesOutput 模型接口契约
- [ ] 多模型融合（残差修正 / BMA 加权）
- [ ] 工程调度 NSGA-II 多目标优化升级
- [ ] LangGraph 多 Agent DAG 编排 + DeepSeek API 接入
- [ ] 自然语言 → 地图操控联动（WebSocket Function Calling）
- [ ] 数字孪生三维场景（Cesium 流域建模 + 洪水淹没动态仿真）
- [ ] 防汛简报自动生成
- [ ] 移动端 H5 / 小程序（Vue3 + Uni-app）

**里程碑 M4：** 完整 AI 平台，Beta 版对外发布

---

### 阶段五：生产就绪（第 11-12 月）

**目标：** 可交付生产系统，通过安全合规验收

- [ ] Kubernetes 生产环境部署（Helm Chart 编写）
- [ ] 性能压测（JMeter）与瓶颈优化
- [ ] 安全加固（等保 2.0 二级 / 三级）
- [ ] 灾备方案实施（数据异步复制 + 容灾演练）
- [ ] 完整技术文档（架构文档 / API 文档 / 运维手册）
- [ ] 用户培训与交付验收

**里程碑 M5：** 生产系统交付，SLA ≥ 99.9%

---

## 十一、非功能性要求

### 性能指标

| 指标 | 目标值 |
|------|--------|
| 大屏页面加载时间 | < 3 秒 |
| WebSocket 推送延迟 | < 500ms |
| API 接口 P99 响应时间 | < 200ms |
| Kafka 消息处理吞吐 | > 10 万条/秒 |
| 多目标优化响应时间 | < 30 秒（100个水库，72h预见期）|
| 系统可用性 SLA | ≥ 99.9% |
| 并发在线用户 | ≥ 500 |

### 高可用设计

- **微服务无状态：** 所有服务实例无状态，支持水平弹性扩缩容
- **数据库主从：** PostgreSQL 一主两从 + 读写分离；InfluxDB 集群模式
- **Redis 哨兵：** 防止缓存单点故障
- **Kafka 多副本：** Replication Factor = 3，ISR 机制防消息丢失
- **多区域容灾：** 核心数据实时复制到灾备中心，RTO < 1小时，RPO < 5分钟
- **断网续传：** 边缘网关本地缓冲队列，网络恢复后自动补传

### 安全要求

- 数据传输全程 TLS 1.3 加密
- 敏感操作双因素认证（2FA）
- 操作日志全量审计，不可删改
- 数据库字段级脱敏（涉密数据）
- 等保 2.0 二级 / 三级认证
- 定期渗透测试 + 自动漏洞扫描

---

## 十二、可扩展增值模块

### 扩展模块优先级矩阵

| 优先级 | 模块 | 说明 |
|--------|------|------|
| 🔴 高 | 气象融合预报 | 接入 ECMWF/CMA，雷达外推 + 数值模式融合 |
| 🔴 高 | 移动端巡查 App | Uni-app，现场打卡、隐患上报 |
| 🟡 中 | 社会损失评估 | 淹没范围 × 人口/资产 GIS 叠加分析 |
| 🟡 中 | 视频 AI 识别 | YOLO 水位自动识别、险情图像分类 |
| 🟡 中 | 知识图谱 | 历史洪水案例图谱 + 相似事件检索 |
| 🟢 低 | 无人机任务系统 | 巡查路线规划 + AI 识别联动 |
| 🟢 低 | 开放 API 平台 | 第三方数据接入标准接口 |
| 🟢 低 | 多语言国际化 | i18n，面向国际合作项目 |

### 气象融合预报（重点扩展）

```
数据源：
  ECMWF ERA5 / CMA GRAPES（GRIB2 格式）
  气象雷达外推（Z-R 关系 → 降雨强度）
      │
      ▼
集合预报框架：
  ├── 雷达外推：0~6 小时短临预报（精度高，时效短）
  ├── 数值模式：6~72 小时中期预报（时效长，精度中等）
  └── 集成融合：贝叶斯模型平均（BMA）加权组合
      │
      ▼
输出：概率性预报（10th / 50th / 90th 分位数）
  → 驱动多目标优化模型的输入不确定性分析
```

---

## 总结

| 关键决策点 | 建议 |
|-----------|------|
| **「数据池」实现** | Kafka（接入）+ Flink（清洗）+ InfluxDB（存储）三层管道，工程级标准做法 |
| **AI 推理部署** | Python FastAPI 独立微服务，避免 JVM 上 ML 运行效率问题 |
| **多目标优化** | 离线 NSGA-III 生成帕累托前沿，在线 DRL 快速检索推荐方案 |
| **Agentic 分步** | Mock Demo（Phase 1）→ 单 Agent + DeepSeek API（Phase 2）→ 多模型服务（Phase 3）→ LangGraph 多 Agent DAG 协同（Phase 4）|
| **容器化策略** | 从第一天起使用 Docker，Phase 5 迁移 Kubernetes，CI/CD 贯穿始终 |
| **优先保障数据链路** | 数据管道是所有上层功能基础，Phase 1-2 重点投入，确保稳定后再推进功能 |

---

*文档版本 v1.0 · Vue 3 + Spring Boot + Spring Cloud 架构*
