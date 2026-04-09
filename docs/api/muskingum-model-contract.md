# 分段马斯金根模型接口契约（Demo）

> 模块：水文模型（分段马斯金根法）
> Java 入口：`backend/optimization-service`
> Python 计算：`python-services/optimization-api`

## 1. 参数率定

- Method: `POST`
- Path: `/api/hydrology/muskingum/calibrate`
- 说明：基于三站洪水过程（上游 A、上游 B、下游 C）进行分段马斯金根参数率定。

### Request Body

```json
{
  "dataset": {
    "upstream_a": "2021_maskingun_three_stations_sheet2_A.csv",
    "upstream_b": "2021_maskingun_three_stations_sheet3_B.csv",
    "downstream_c": "2021_maskingun_three_stations_sheet1_C.csv"
  },
  "dt_minutes": 60,
  "train_ratio": 0.7,
  "segments": 3,
  "iterations": 3500
}
```

### Response Body（关键字段）

```json
{
  "success": true,
  "algorithm": "Segmented Muskingum + Random Search",
  "sample_count": 1200,
  "train_count": 840,
  "test_count": 360,
  "calibration": {
    "dt_minutes": 60,
    "train_ratio": 0.7,
    "segments": 3,
    "thresholds": [1200.0, 2300.0],
    "weights": { "A": 0.46, "B": 0.54 },
    "params": [
      { "k_hours": 3.2, "x": 0.18 },
      { "k_hours": 4.8, "x": 0.22 },
      { "k_hours": 6.5, "x": 0.27 }
    ]
  },
  "metrics": {
    "train_rmse": 120.5,
    "train_nse": 0.89,
    "test_rmse": 148.2,
    "test_nse": 0.84,
    "test_mape": 7.35
  },
  "series": {
    "time": ["2021-10-01T00:00:00"],
    "A": [900.0],
    "B": [760.0],
    "C_obs": [1800.0],
    "C_sim": [1750.0]
  }
}
```

## 2. 流量预报

- Method: `POST`
- Path: `/api/hydrology/muskingum/forecast`
- 说明：基于已率定参数执行下游流量预报（Demo 下可使用最近一次率定结果）。

### Request Body

```json
{
  "dataset": {
    "upstream_a": "2021_maskingun_three_stations_sheet2_A.csv",
    "upstream_b": "2021_maskingun_three_stations_sheet3_B.csv",
    "downstream_c": "2021_maskingun_three_stations_sheet1_C.csv"
  },
  "forecast_steps": 72,
  "use_last_calibration": true
}
```

### Response Body（关键字段）

```json
{
  "success": true,
  "model": "Segmented Muskingum",
  "dt_minutes": 60,
  "used_steps": 72,
  "metrics": {
    "forecast_rmse": 155.1,
    "forecast_nse": 0.82,
    "forecast_mape": 8.01
  },
  "series": {
    "time": ["2021-10-15T00:00:00"],
    "A": [780.0],
    "B": [650.0],
    "C_obs": [1410.0],
    "C_forecast": [1360.0]
  }
}
```

## 3. 约束与说明

- `segments` 建议范围：`2 ~ 6`。
- `train_ratio` 建议范围：`(0.5, 0.95)`。
- 当前优化算法为随机搜索 + 局部搜索（Demo），后续可替换为 DE/PSO/贝叶斯优化。
- 当前数据来源默认是 `dataset/maskingun/` 下三站 CSV。

## 4. 已知逻辑问题（2026-04-09）

- 当前 Demo 拓扑假设为 `A/B 并联汇流 -> 单河段 -> C`，并通过固定权重将 A、B 合成为单一入流。
- 该实现能够跑通端到端链路，但未显式建模 `A->汇流点` 与 `B->汇流点` 的独立传播时滞与河段参数差异。
- 在复杂洪峰过程下，单入流简化会放大相位误差，可能导致 NSE 偏低或为负。

### 修正方向（下一阶段）

- 将单河段结构升级为两支路 + 主河道的多河段拓扑。
- 为每条支路独立率定 Muskingum 参数（`K`, `x`），并加入支路汇流时滞参数。
- 在汇流节点后再执行主河道演算，形成 `A 段 + B 段 + C 段` 的分层率定流程。
- 新增分段策略开关：`single_reach`（兼容现状）与 `multi_reach`（增强模式）。
