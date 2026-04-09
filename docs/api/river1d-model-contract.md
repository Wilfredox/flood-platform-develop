# River1D 模型数据接口契约（Draft）

> 模块：R10 后端模型数据接口草案  
> 服务：`backend/optimization-service`  
> Base URL：`/api/river1d/projects`

## 1. 保存草案

- Method: `POST`
- Path: `/draft`
- 说明：接收前端 River1D 工作台当前项目数据，保存 Draft（当前为内存存储）。

### Request Body

```json
{
  "projectName": "武汉段一维河网方案",
  "crs": "CGCS2000_3TM_120",
  "description": "Demo 草案",
  "rivers": [
    {
      "id": "river-001",
      "name": "长江主槽",
      "coords": [
        { "lat": 30.52, "lng": 114.28 },
        { "lat": 30.50, "lng": 114.36 }
      ]
    }
  ],
  "banks": [],
  "sections": [
    {
      "id": "sec-001",
      "name": "CS-001",
      "station": 1200.0,
      "coords": [
        { "lat": 30.505, "lng": 114.30 },
        { "lat": 30.495, "lng": 114.31 }
      ],
      "profile": [
        { "dist": 0.0, "elev": 22.4 },
        { "dist": 30.0, "elev": 20.8 },
        { "dist": 60.0, "elev": 21.2 }
      ]
    }
  ],
  "structures": [],
  "nodes": [
    {
      "id": "N001",
      "lat": 30.52,
      "lng": 114.28,
      "nodeType": "upstream"
    }
  ]
}
```

### Response Body

```json
{
  "projectId": "b2824810-11e6-4899-9c64-2f2dfb1f487f",
  "projectName": "武汉段一维河网方案",
  "status": "DRAFT_SAVED",
  "riverCount": 1,
  "sectionCount": 1,
  "structureCount": 0,
  "message": "River1D 草案保存成功"
}
```

## 2. 获取草案

- Method: `GET`
- Path: `/draft/{projectId}`
- 说明：按 `projectId` 读取已保存的 Draft。

### Response Body

```json
{
  "projectId": "b2824810-11e6-4899-9c64-2f2dfb1f487f",
  "project": {
    "projectName": "武汉段一维河网方案",
    "crs": "CGCS2000_3TM_120",
    "description": "Demo 草案",
    "rivers": [],
    "banks": [],
    "sections": [],
    "structures": [],
    "nodes": []
  },
  "status": "DRAFT_LOADED"
}
```

## 3. 拓扑检查

- Method: `POST`
- Path: `/topology/check`
- 说明：支持两种输入方式：
  1) 传 `projectId`（后端读取已存 Draft）
  2) 直接传 `project`（即时校验，不依赖存储）

### Request Body（按 projectId 校验）

```json
{
  "projectId": "b2824810-11e6-4899-9c64-2f2dfb1f487f",
  "project": null
}
```

### Response Body

```json
{
  "ok": true,
  "riverCount": 1,
  "sectionCount": 1,
  "nodeCount": 1,
  "issues": [],
  "warnings": []
}
```

## 4. 字段约束（Draft 版）

- `projectName`: 必填，建议 <= 64 字符。
- `crs`: 推荐枚举：`CGCS2000_3TM_108/111/114/117/120/123`。
- `coords`: 每条线要素建议至少 2 个点。
- `sections[].profile`: 建议至少 2 个点；否则返回 warning。
- `nodeType`: 推荐值 `upstream | downstream | junction`。

## 5. 版本与后续

- 当前状态：Draft，内存存储，不具备持久化与并发控制。

## 6. 启动计算任务（R11）

- Method: `POST`
- Path: `/compute/run`
- 说明：提交 River1D 项目数据并启动 Mock 计算任务，返回 `taskId`。

### Request Body

```json
{
  "projectId": null,
  "project": {
    "projectName": "武汉段一维河网方案",
    "crs": "CGCS2000_3TM_120",
    "description": "Demo 草案",
    "rivers": [],
    "banks": [],
    "sections": [],
    "structures": [],
    "nodes": []
  },
  "params": {
    "mainChannelN": 0.03,
    "dtSeconds": 60,
    "totalHours": 24
  }
}
```

### Response Body

```json
{
  "taskId": "3f741fa4-8788-4a48-a49d-dfc4f7f6b6cc",
  "projectId": "7c20af2f-f37d-4f51-bf26-fd89ce6e08f0",
  "status": "RUNNING",
  "message": "River1D 计算任务已启动（Mock）"
}
```

## 7. 查询计算状态（R11）

- Method: `GET`
- Path: `/compute/{taskId}/status`
- 说明：返回计算进度、阶段和日志（Mock）。

### Response Body

```json
{
  "taskId": "3f741fa4-8788-4a48-a49d-dfc4f7f6b6cc",
  "projectId": "7c20af2f-f37d-4f51-bf26-fd89ce6e08f0",
  "status": "RUNNING",
  "progress": 58,
  "stage": "组装断面与边界条件",
  "logs": [
    "[INFO] 任务已创建，开始校验输入数据...",
    "[INFO] 网格与河道节点加载完成",
    "[INFO] 拓扑关系检查通过，未发现致命错误",
    "[INFO] 断面 profile 与糙率参数装载完成"
  ],
  "startedAt": "1775123000000",
  "finishedAt": null
}
```

## 8. 后续

- 后续可从轮询升级为 WebSocket/SSE 实时日志推送。
- 后续可将 Mock 阶段映射为真实计算引擎阶段。
