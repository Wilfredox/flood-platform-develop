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
  "routing_mode": "multi_reach",
  "iterations": 3500
}
```

### Response Body（关键字段）

```json
{
  "success": true,
  "algorithm": "Segmented Muskingum (multi_reach) + Random Search",
  "sample_count": 1200,
  "train_count": 840,
  "test_count": 360,
  "calibration": {
    "dt_minutes": 60,
    "train_ratio": 0.7,
    "segments": 3,
    "thresholds": [1200.0, 2300.0],
    "weights": { "A": 0.46, "B": 0.54 },
    "routing_mode": "multi_reach",
    "thresholds_a": [1150.0, 2100.0],
    "thresholds_b": [980.0, 1850.0],
    "params_a": [
      { "k_hours": 2.8, "x": 0.16 },
      { "k_hours": 4.2, "x": 0.21 },
      { "k_hours": 6.0, "x": 0.25 }
    ],
    "params_b": [
      { "k_hours": 3.4, "x": 0.18 },
      { "k_hours": 4.9, "x": 0.23 },
      { "k_hours": 6.8, "x": 0.28 }
    ],
    "total_gain": 1.02,
    "baseflow": 12.5,
    "bias": 6.2,
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
  },
  "full_series": {
    "time": ["2021-09-01T00:00:00"],
    "A": [820.0],
    "B": [710.0],
    "C_obs": [1650.0],
    "C_sim": [1605.0]
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
  "model": "Segmented Muskingum (multi_reach)",
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
  },
  "full_series": {
    "time": ["2021-09-01T00:00:00"],
    "A": [820.0],
    "B": [710.0],
    "C_obs": [1650.0],
    "C_forecast": [1608.0]
  }
}
```

## 3. 约束与说明

- `segments` 建议范围：`2 ~ 6`。
- `train_ratio` 建议范围：`(0.5, 0.95)`。
- `routing_mode`：
  - `single_reach`：A/B 先按权重汇流，再单河段分段马斯金根演进（兼容模式）。
  - `multi_reach`：A、B 两支路独立分段演进后再叠加 `baseflow+bias`（推荐模式）。
- `total_gain`：`multi_reach` 下的总增益系数，用于约束整体量级漂移。
- `series`：末段窗口数据（用于“末段预报曲线”）。
- `full_series`：完整样本时段数据（用于“完整过程线”）。
- 当前优化算法为随机搜索 + 局部搜索（Demo），后续可替换为 DE/PSO/贝叶斯优化。
- 当前数据来源默认是 `dataset/maskingun/` 下三站 CSV。

## 4. 已知逻辑问题（2026-04-10）

- 已升级为 `multi_reach`（A/B 独立分段演进），但在部分样本切分下仍可能出现测试 NSE<0。
- 当前随机搜索策略仍可能产生偏大的 `bias` 与边界化 `total_gain`，导致泛化不稳定。
- 训练集与测试集工况差异较大时，存在明显过拟合风险。

### 修正方向（下一阶段）

- 将单河段结构升级为两支路 + 主河道的多河段拓扑。
- 为每条支路独立率定 Muskingum 参数（`K`, `x`），并补充支路时滞参数率定。
- 在汇流节点后再执行主河道演算，形成 `A 段 + B 段 + C 段` 的分层率定流程。
- 保留分段策略开关：`single_reach`（兼容）与 `multi_reach`（增强）。
