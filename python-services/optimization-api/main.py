"""
M06 Python 优化调度 API
1) NSGA-II Mock 调度能力
2) 分段马斯金根法参数率定与流量预报能力
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import random

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="洪水优化调度服务",
    description="基于 NSGA-II 与分段马斯金根法的优化与洪水演进服务",
    version="0.1.0-demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 数据模型 ----------

class OptimizeRequest(BaseModel):
    station_id: str = "ST001"
    forecast_hours: int = 24
    population_size: int = 100
    generations: int = 200
    objectives: List[str] = ["min_flood_risk", "min_eco_cost"]


class GateOpening(BaseModel):
    gate_id: str
    opening_ratio: float  # 0.0 ~ 1.0


class ParetoSolution(BaseModel):
    id: int
    flood_risk: float
    ecological_cost: float
    gate_openings: List[GateOpening]
    recommended: bool = False


class OptimizeResponse(BaseModel):
    success: bool
    algorithm: str
    generations: int
    solution_count: int
    solutions: List[ParetoSolution]


class MuskingumDatasetConfig(BaseModel):
    upstream_a: str = "2021_maskingun_three_stations_sheet2_A.csv"
    upstream_b: str = "2021_maskingun_three_stations_sheet3_B.csv"
    downstream_c: str = "2021_maskingun_three_stations_sheet1_C.csv"


class MuskingumSegmentParam(BaseModel):
    k_hours: float
    x: float


class MuskingumCalibrationSnapshot(BaseModel):
    dt_minutes: int
    train_ratio: float
    segments: int
    thresholds: List[float]
    weights: Dict[str, float]
    params: List[MuskingumSegmentParam]
    routing_mode: str = "single_reach"
    thresholds_a: List[float] | None = None
    thresholds_b: List[float] | None = None
    params_a: List[MuskingumSegmentParam] | None = None
    params_b: List[MuskingumSegmentParam] | None = None
    total_gain: float = 1.0
    baseflow: float = 0.0
    bias: float = 0.0


class MuskingumCalibrateRequest(BaseModel):
    dataset: MuskingumDatasetConfig = Field(default_factory=MuskingumDatasetConfig)
    dt_minutes: int = 60
    train_ratio: float = 0.7
    segments: int = 3
    routing_mode: str = "multi_reach"
    iterations: int = 3500
    seed: int = 42
    include_series_points: int = 240


class MuskingumCalibrateResponse(BaseModel):
    success: bool
    algorithm: str
    sample_count: int
    train_count: int
    test_count: int
    calibration: MuskingumCalibrationSnapshot
    metrics: Dict[str, float]
    series: Dict[str, List[float | str]]
    full_series: Dict[str, List[float | str]]


class MuskingumForecastRequest(BaseModel):
    dataset: MuskingumDatasetConfig = Field(default_factory=MuskingumDatasetConfig)
    dt_minutes: int | None = None
    forecast_steps: int = 72
    use_last_calibration: bool = True
    calibration: MuskingumCalibrationSnapshot | None = None


class MuskingumForecastResponse(BaseModel):
    success: bool
    model: str
    dt_minutes: int
    used_steps: int
    metrics: Dict[str, float]
    series: Dict[str, List[float | str]]
    full_series: Dict[str, List[float | str]]


LAST_CALIBRATION: MuskingumCalibrationSnapshot | None = None


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_dataset_path(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    local = _workspace_root() / "dataset" / "maskingun" / raw
    if local.exists():
        return local

    relative = (_workspace_root() / raw).resolve()
    if relative.exists():
        return relative

    raise HTTPException(status_code=400, detail=f"数据文件不存在: {raw}")


def _load_series(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        raise HTTPException(status_code=400, detail=f"CSV 列不足 2 列: {path}")

    ts = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    values = pd.to_numeric(df.iloc[:, 1], errors="coerce")
    clean = pd.DataFrame({"t": ts, "q": values}).dropna().sort_values("t")

    if clean.empty:
        raise HTTPException(status_code=400, detail=f"CSV 无有效时序数据: {path}")

    series = pd.Series(clean["q"].values, index=clean["t"].values)
    series = series[~series.index.duplicated(keep="first")].sort_index()
    return series


def _prepare_aligned_data(dataset: MuskingumDatasetConfig, dt_minutes: int) -> pd.DataFrame:
    if dt_minutes <= 0:
        raise HTTPException(status_code=400, detail="dt_minutes 必须 > 0")

    freq = f"{dt_minutes}min"
    a = _load_series(_resolve_dataset_path(dataset.upstream_a)).resample(freq).mean().interpolate("time").ffill().bfill()
    b = _load_series(_resolve_dataset_path(dataset.upstream_b)).resample(freq).mean().interpolate("time").ffill().bfill()
    c = _load_series(_resolve_dataset_path(dataset.downstream_c)).resample(freq).mean().interpolate("time").ffill().bfill()

    start = max(a.index.min(), b.index.min(), c.index.min())
    end = min(a.index.max(), b.index.max(), c.index.max())
    if start >= end:
        raise HTTPException(status_code=400, detail="三站数据时间范围无交集")

    aligned = pd.concat([
        a.loc[start:end].rename("A"),
        b.loc[start:end].rename("B"),
        c.loc[start:end].rename("C"),
    ], axis=1, join="inner").dropna()

    if len(aligned) < 50:
        raise HTTPException(status_code=400, detail="有效样本不足，至少需要 50 条")
    return aligned


def _coeffs(k_hours: float, x: float, dt_hours: float) -> Tuple[float, float, float]:
    den = k_hours - k_hours * x + 0.5 * dt_hours
    if den <= 0:
        raise ValueError("系数分母无效")

    c0 = (-k_hours * x + 0.5 * dt_hours) / den
    c1 = (k_hours * x + 0.5 * dt_hours) / den
    c2 = (k_hours - k_hours * x - 0.5 * dt_hours) / den
    return c0, c1, c2


def _segment_idx(value: float, thresholds: List[float]) -> int:
    idx = 0
    while idx < len(thresholds) and value > thresholds[idx]:
        idx += 1
    return idx


def _simulate_segmented(
    inflow: np.ndarray,
    observed: np.ndarray,
    thresholds: List[float],
    params: List[Tuple[float, float]],
    dt_hours: float,
) -> np.ndarray:
    routed = np.zeros_like(inflow, dtype=float)
    routed[0] = max(0.0, float(observed[0]))

    for i in range(1, len(inflow)):
        seg = _segment_idx(float(inflow[i]), thresholds)
        k_hours, x = params[seg]
        c0, c1, c2 = _coeffs(k_hours, x, dt_hours)
        routed[i] = c0 * inflow[i] + c1 * inflow[i - 1] + c2 * routed[i - 1]
        if routed[i] < 0:
            routed[i] = 0.0

    return routed


def _metrics(obs: np.ndarray, sim: np.ndarray) -> Dict[str, float]:
    eps = 1e-9
    rmse = float(np.sqrt(np.mean((obs - sim) ** 2)))
    mae = float(np.mean(np.abs(obs - sim)))
    den = float(np.sum((obs - np.mean(obs)) ** 2))
    nse = float(1.0 - np.sum((obs - sim) ** 2) / (den + eps))
    mape = float(np.mean(np.abs((obs - sim) / (obs + eps))) * 100.0)
    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "nse": round(nse, 4),
        "mape": round(mape, 4),
    }


def _optimize_segmented(
    inflow_train: np.ndarray,
    obs_train: np.ndarray,
    dt_hours: float,
    segments: int,
    iterations: int,
    seed: int,
) -> tuple[Dict[str, float], List[float], List[Tuple[float, float]], np.ndarray]:
    rng = np.random.default_rng(seed)
    quantiles = [i / segments for i in range(1, segments)]
    thresholds = [float(np.quantile(inflow_train, q)) for q in quantiles]

    k_min = max(dt_hours * 0.6, 0.2)
    k_max = 72.0

    def decode(vec: np.ndarray) -> tuple[Dict[str, float], List[Tuple[float, float]]]:
        wa_raw = float(np.clip(vec[0], 0.01, 1.0))
        wb_raw = float(np.clip(vec[1], 0.01, 1.0))
        total = wa_raw + wb_raw
        weights = {"A": wa_raw / total, "B": wb_raw / total}

        params: List[Tuple[float, float]] = []
        cursor = 2
        for _ in range(segments):
            k_hours = float(np.clip(vec[cursor], k_min, k_max))
            x = float(np.clip(vec[cursor + 1], 0.0, 0.49))
            params.append((k_hours, x))
            cursor += 2
        return weights, params

    def objective(vec: np.ndarray) -> tuple[float, np.ndarray, Dict[str, float], List[Tuple[float, float]]]:
        try:
            weights, params = decode(vec)
            inflow_mix = weights["A"] * inflow_train[:, 0] + weights["B"] * inflow_train[:, 1]
            sim = _simulate_segmented(inflow_mix, obs_train, thresholds, params, dt_hours)

            # 额外平滑惩罚，降低不合理锯齿
            rough_obs = np.mean(np.abs(np.diff(obs_train))) + 1e-6
            rough_sim = np.mean(np.abs(np.diff(sim)))
            rough_penalty = max(0.0, rough_sim - rough_obs) * 0.03

            rmse = float(np.sqrt(np.mean((obs_train - sim) ** 2)))
            return rmse + rough_penalty, sim, weights, params
        except Exception:
            return 1e12, np.zeros_like(obs_train), {"A": 0.5, "B": 0.5}, [(k_min, 0.2)] * segments

    dim = 2 + 2 * segments
    best_vec = None
    best_score = 1e15
    best_sim = None
    best_weights = None
    best_params = None

    global_steps = max(200, int(iterations * 0.75))
    local_steps = max(80, iterations - global_steps)

    for _ in range(global_steps):
        vec = np.zeros(dim, dtype=float)
        vec[0] = rng.uniform(0.05, 0.95)
        vec[1] = rng.uniform(0.05, 0.95)
        cursor = 2
        for _ in range(segments):
            vec[cursor] = rng.uniform(k_min, k_max)
            vec[cursor + 1] = rng.uniform(0.0, 0.49)
            cursor += 2

        score, sim, weights, params = objective(vec)
        if score < best_score:
            best_score = score
            best_vec = vec
            best_sim = sim
            best_weights = weights
            best_params = params

    if best_vec is None:
        raise HTTPException(status_code=500, detail="率定失败，未找到有效参数")

    scales = np.array([0.05, 0.05] + [6.0, 0.06] * segments)
    for _ in range(local_steps):
        noise = rng.normal(0.0, 1.0, size=dim)
        cand = best_vec + noise * scales
        score, sim, weights, params = objective(cand)
        if score < best_score:
            best_score = score
            best_vec = cand
            best_sim = sim
            best_weights = weights
            best_params = params
            scales = np.maximum(scales * 0.98, 1e-3)

    return best_weights, thresholds, best_params, best_sim


def _simulate_multi_reach(
    inflow_a: np.ndarray,
    inflow_b: np.ndarray,
    observed: np.ndarray,
    thresholds_a: List[float],
    thresholds_b: List[float],
    params_a: List[Tuple[float, float]],
    params_b: List[Tuple[float, float]],
    dt_hours: float,
    weight_a: float,
    weight_b: float,
    total_gain: float,
    baseflow: float,
    bias: float,
) -> np.ndarray:
    out_a = _simulate_segmented(inflow_a, observed, thresholds_a, params_a, dt_hours)
    out_b = _simulate_segmented(inflow_b, observed, thresholds_b, params_b, dt_hours)

    n = len(inflow_a)
    t_arr = np.arange(n, dtype=float)
    trend = bias * (t_arr / max(1.0, float(n - 1)))
    sim = total_gain * (weight_a * out_a + weight_b * out_b) + baseflow + trend
    return np.maximum(sim, 0.0)


def _optimize_multi_reach(
    inflow_a_train: np.ndarray,
    inflow_b_train: np.ndarray,
    obs_train: np.ndarray,
    dt_hours: float,
    segments: int,
    iterations: int,
    seed: int,
) -> tuple[Dict[str, float], float, List[float], List[float], List[Tuple[float, float]], List[Tuple[float, float]], float, float, np.ndarray]:
    rng = np.random.default_rng(seed)
    quantiles = [i / segments for i in range(1, segments)]
    thresholds_a = [float(np.quantile(inflow_a_train, q)) for q in quantiles]
    thresholds_b = [float(np.quantile(inflow_b_train, q)) for q in quantiles]

    k_min = max(dt_hours * 0.6, 0.2)
    k_max = 72.0

    obs_q10 = float(np.quantile(obs_train, 0.10))
    obs_q90 = float(np.quantile(obs_train, 0.90))
    obs_std = float(np.std(obs_train)) + 1e-6
    baseflow_max = max(5.0, obs_q10 * 0.5)
    bias_abs = max(5.0, (obs_q90 - obs_q10) * 0.25)

    def decode(vec: np.ndarray) -> tuple[Dict[str, float], float, List[Tuple[float, float]], List[Tuple[float, float]], float, float]:
        wa_raw = float(np.clip(vec[0], 0.05, 1.0))
        wb_raw = float(np.clip(vec[1], 0.05, 1.0))
        total = wa_raw + wb_raw
        weights = {"A": wa_raw / total, "B": wb_raw / total}
        total_gain = float(np.clip(vec[2], 0.6, 1.6))

        params_a: List[Tuple[float, float]] = []
        params_b: List[Tuple[float, float]] = []

        cursor = 3
        for _ in range(segments):
            ka = float(np.clip(vec[cursor], k_min, k_max))
            xa = float(np.clip(vec[cursor + 1], 0.0, 0.49))
            params_a.append((ka, xa))
            cursor += 2

        for _ in range(segments):
            kb = float(np.clip(vec[cursor], k_min, k_max))
            xb = float(np.clip(vec[cursor + 1], 0.0, 0.49))
            params_b.append((kb, xb))
            cursor += 2

        baseflow = float(np.clip(vec[cursor], 0.0, baseflow_max))
        bias = float(np.clip(vec[cursor + 1], -bias_abs, bias_abs))
        return weights, total_gain, params_a, params_b, baseflow, bias

    def objective(vec: np.ndarray) -> tuple[float, np.ndarray, Dict[str, float], float, List[Tuple[float, float]], List[Tuple[float, float]], float, float]:
        try:
            weights, total_gain, params_a, params_b, baseflow, bias = decode(vec)
            sim = _simulate_multi_reach(
                inflow_a_train,
                inflow_b_train,
                obs_train,
                thresholds_a,
                thresholds_b,
                params_a,
                params_b,
                dt_hours,
                weights["A"],
                weights["B"],
                total_gain,
                baseflow,
                bias,
            )

            split_idx = max(30, int(len(obs_train) * 0.8))
            split_idx = min(split_idx, len(obs_train) - 10)
            obs_fit = obs_train[:split_idx]
            sim_fit = sim[:split_idx]
            obs_val = obs_train[split_idx:]
            sim_val = sim[split_idx:]

            rough_obs = np.mean(np.abs(np.diff(obs_train))) + 1e-6
            rough_sim = np.mean(np.abs(np.diff(sim)))
            rough_penalty = max(0.0, rough_sim - rough_obs) * 0.03
            rmse_fit = float(np.sqrt(np.mean((obs_fit - sim_fit) ** 2)))
            rmse_val = float(np.sqrt(np.mean((obs_val - sim_val) ** 2)))
            gap_penalty = max(0.0, rmse_val - rmse_fit) * 0.2
            bias_penalty = (abs(bias) / obs_std) * 0.03
            gain_penalty = abs(total_gain - 1.0) * 2.0

            score = (0.65 * rmse_fit) + (0.35 * rmse_val) + rough_penalty + gap_penalty + bias_penalty + gain_penalty
            return score, sim, weights, total_gain, params_a, params_b, baseflow, bias
        except Exception:
            fallback = [(k_min, 0.2)] * segments
            return 1e12, np.zeros_like(obs_train), {"A": 0.5, "B": 0.5}, 1.0, fallback, fallback, 0.0, 0.0

    dim = 4 * segments + 5
    best_vec = None
    best_score = 1e15
    best_sim = None
    best_weights = {"A": 0.5, "B": 0.5}
    best_total_gain = 1.0
    best_params_a = None
    best_params_b = None
    best_baseflow = 0.0
    best_bias = 0.0

    global_steps = max(240, int(iterations * 0.75))
    local_steps = max(80, iterations - global_steps)

    for _ in range(global_steps):
        vec = np.zeros(dim, dtype=float)
        vec[0] = rng.uniform(0.05, 0.95)
        vec[1] = rng.uniform(0.05, 0.95)
        vec[2] = rng.uniform(0.7, 1.4)

        cursor = 3
        for _ in range(segments):
            vec[cursor] = rng.uniform(k_min, k_max)
            vec[cursor + 1] = rng.uniform(0.0, 0.49)
            cursor += 2
        for _ in range(segments):
            vec[cursor] = rng.uniform(k_min, k_max)
            vec[cursor + 1] = rng.uniform(0.0, 0.49)
            cursor += 2
        vec[cursor] = rng.uniform(0.0, baseflow_max)
        vec[cursor + 1] = rng.uniform(-bias_abs, bias_abs)

        score, sim, weights, total_gain, params_a, params_b, baseflow, bias = objective(vec)
        if score < best_score:
            best_score = score
            best_vec = vec
            best_sim = sim
            best_weights = weights
            best_total_gain = total_gain
            best_params_a = params_a
            best_params_b = params_b
            best_baseflow = baseflow
            best_bias = bias

    if best_vec is None:
        raise HTTPException(status_code=500, detail="率定失败，未找到有效参数")

    scales = np.array([0.08, 0.08, 0.12] + [6.0, 0.06] * (2 * segments) + [max(2.0, baseflow_max * 0.12), max(1.0, bias_abs * 0.1)])
    for _ in range(local_steps):
        noise = rng.normal(0.0, 1.0, size=dim)
        cand = best_vec + noise * scales
        score, sim, weights, total_gain, params_a, params_b, baseflow, bias = objective(cand)
        if score < best_score:
            best_score = score
            best_vec = cand
            best_sim = sim
            best_weights = weights
            best_total_gain = total_gain
            best_params_a = params_a
            best_params_b = params_b
            best_baseflow = baseflow
            best_bias = bias
            scales = np.maximum(scales * 0.98, 1e-3)

    return best_weights, best_total_gain, thresholds_a, thresholds_b, best_params_a, best_params_b, best_baseflow, best_bias, best_sim


# ---------- 路由 ----------

@app.post("/optimize/run", response_model=OptimizeResponse)
async def run_optimization(req: OptimizeRequest):
    """
    触发多目标优化 (Demo 返回 Mock Pareto 前沿)
    正式版将调用 pymoo / DEAP 运行 NSGA-II
    """
    random.seed(42)
    solutions: List[ParetoSolution] = []

    n = min(req.population_size, 30)  # Demo 限制解数量
    for i in range(n):
        t = i / max(n - 1, 1)
        flood_risk = round(0.05 + 0.30 * t + random.gauss(0, 0.015), 4)
        eco_cost = round(0.90 - 0.55 * t + random.gauss(0, 0.02), 4)

        gates = [
            GateOpening(gate_id="G1", opening_ratio=round(0.2 + random.random() * 0.6, 3)),
            GateOpening(gate_id="G2", opening_ratio=round(0.1 + random.random() * 0.7, 3)),
            GateOpening(gate_id="G3", opening_ratio=round(0.15 + random.random() * 0.5, 3)),
        ]

        solutions.append(ParetoSolution(
            id=i + 1,
            flood_risk=flood_risk,
            ecological_cost=eco_cost,
            gate_openings=gates,
            recommended=(i == n // 3),  # 约 1/3 处为推荐解
        ))

    return OptimizeResponse(
        success=True,
        algorithm="NSGA-II (Mock)",
        generations=req.generations,
        solution_count=len(solutions),
        solutions=solutions,
    )


@app.post("/hydrology/muskingum/calibrate", response_model=MuskingumCalibrateResponse)
async def calibrate_muskingum(req: MuskingumCalibrateRequest):
    global LAST_CALIBRATION

    if req.segments < 2 or req.segments > 6:
        raise HTTPException(status_code=400, detail="segments 建议在 2~6 之间")
    if req.iterations < 200:
        raise HTTPException(status_code=400, detail="iterations 至少为 200")
    if req.train_ratio <= 0.5 or req.train_ratio >= 0.95:
        raise HTTPException(status_code=400, detail="train_ratio 建议在 (0.5, 0.95)")
    if req.routing_mode not in {"single_reach", "multi_reach"}:
        raise HTTPException(status_code=400, detail="routing_mode 仅支持 single_reach 或 multi_reach")

    aligned = _prepare_aligned_data(req.dataset, req.dt_minutes)
    sample_count = len(aligned)
    train_count = int(sample_count * req.train_ratio)
    if train_count < 30 or sample_count - train_count < 15:
        raise HTTPException(status_code=400, detail="训练/验证样本不足，请调整 train_ratio 或 dt")

    dt_hours = req.dt_minutes / 60.0
    inflow_all = aligned[["A", "B"]].values.astype(float)
    outflow_all = aligned["C"].values.astype(float)

    inflow_train = inflow_all[:train_count]
    outflow_train = outflow_all[:train_count]

    weights = {"A": 0.5, "B": 0.5}
    thresholds: List[float] = []
    params: List[Tuple[float, float]] = []
    thresholds_a: List[float] | None = None
    thresholds_b: List[float] | None = None
    params_a: List[Tuple[float, float]] | None = None
    params_b: List[Tuple[float, float]] | None = None
    baseflow = 0.0
    bias = 0.0

    if req.routing_mode == "single_reach":
        weights, thresholds, params, _ = _optimize_segmented(
            inflow_train,
            outflow_train,
            dt_hours,
            req.segments,
            req.iterations,
            req.seed,
        )
        inflow_mix_all = weights["A"] * inflow_all[:, 0] + weights["B"] * inflow_all[:, 1]
        sim_all = _simulate_segmented(inflow_mix_all, outflow_all, thresholds, params, dt_hours)
    else:
        weights, total_gain, thresholds_a, thresholds_b, params_a, params_b, baseflow, bias, _ = _optimize_multi_reach(
            inflow_train[:, 0],
            inflow_train[:, 1],
            outflow_train,
            dt_hours,
            req.segments,
            req.iterations,
            req.seed,
        )
        sim_all = _simulate_multi_reach(
            inflow_all[:, 0],
            inflow_all[:, 1],
            outflow_all,
            thresholds_a,
            thresholds_b,
            params_a,
            params_b,
            dt_hours,
            weights["A"],
            weights["B"],
            total_gain,
            baseflow,
            bias,
        )
        # 为兼容既有前端表格，保留一组可展示段参数（A 支路）
        thresholds = thresholds_a
        params = params_a

    obs_train = outflow_all[:train_count]
    pred_train = sim_all[:train_count]
    obs_test = outflow_all[train_count:]
    pred_test = sim_all[train_count:]

    metric_train = _metrics(obs_train, pred_train)
    metric_test = _metrics(obs_test, pred_test)

    calibration = MuskingumCalibrationSnapshot(
        dt_minutes=req.dt_minutes,
        train_ratio=req.train_ratio,
        segments=req.segments,
        thresholds=[round(v, 4) for v in thresholds],
        weights={"A": round(weights["A"], 6), "B": round(weights["B"], 6)},
        params=[MuskingumSegmentParam(k_hours=round(k, 6), x=round(x, 6)) for k, x in params],
        routing_mode=req.routing_mode,
        thresholds_a=[round(v, 4) for v in thresholds_a] if thresholds_a is not None else None,
        thresholds_b=[round(v, 4) for v in thresholds_b] if thresholds_b is not None else None,
        params_a=[MuskingumSegmentParam(k_hours=round(k, 6), x=round(x, 6)) for k, x in params_a] if params_a is not None else None,
        params_b=[MuskingumSegmentParam(k_hours=round(k, 6), x=round(x, 6)) for k, x in params_b] if params_b is not None else None,
        total_gain=round(total_gain, 6) if req.routing_mode == "multi_reach" else 1.0,
        baseflow=round(baseflow, 6),
        bias=round(bias, 6),
    )
    LAST_CALIBRATION = calibration

    keep = max(60, min(req.include_series_points, sample_count))
    tail = aligned.iloc[-keep:]
    tail_sim = sim_all[-keep:]

    return MuskingumCalibrateResponse(
        success=True,
        algorithm=f"Segmented Muskingum ({req.routing_mode}) + Random Search",
        sample_count=sample_count,
        train_count=train_count,
        test_count=sample_count - train_count,
        calibration=calibration,
        metrics={
            "train_rmse": metric_train["rmse"],
            "train_nse": metric_train["nse"],
            "test_rmse": metric_test["rmse"],
            "test_nse": metric_test["nse"],
            "test_mape": metric_test["mape"],
        },
        series={
            "time": [t.isoformat() for t in tail.index.to_pydatetime()],
            "A": [round(float(v), 4) for v in tail["A"].tolist()],
            "B": [round(float(v), 4) for v in tail["B"].tolist()],
            "C_obs": [round(float(v), 4) for v in tail["C"].tolist()],
            "C_sim": [round(float(v), 4) for v in tail_sim.tolist()],
        },
        full_series={
            "time": [t.isoformat() for t in aligned.index.to_pydatetime()],
            "A": [round(float(v), 4) for v in aligned["A"].tolist()],
            "B": [round(float(v), 4) for v in aligned["B"].tolist()],
            "C_obs": [round(float(v), 4) for v in aligned["C"].tolist()],
            "C_sim": [round(float(v), 4) for v in sim_all.tolist()],
        },
    )


@app.post("/hydrology/muskingum/forecast", response_model=MuskingumForecastResponse)
async def forecast_muskingum(req: MuskingumForecastRequest):
    calibration = req.calibration
    if calibration is None and req.use_last_calibration:
        calibration = LAST_CALIBRATION
    if calibration is None:
        raise HTTPException(status_code=400, detail="缺少 calibration，请先调用 /hydrology/muskingum/calibrate")

    dt_minutes = req.dt_minutes if req.dt_minutes is not None else calibration.dt_minutes
    aligned = _prepare_aligned_data(req.dataset, dt_minutes)

    inflow_all = aligned[["A", "B"]].values.astype(float)
    outflow_all = aligned["C"].values.astype(float)
    weights = calibration.weights
    params = [(p.k_hours, p.x) for p in calibration.params]

    if len(params) != calibration.segments:
        raise HTTPException(status_code=400, detail="calibration 参数段数与配置不一致")

    dt_hours = dt_minutes / 60.0
    if calibration.routing_mode == "multi_reach":
        if not calibration.thresholds_a or not calibration.thresholds_b or not calibration.params_a or not calibration.params_b:
            raise HTTPException(status_code=400, detail="multi_reach 缺少支路参数，请重新率定")
        params_a = [(p.k_hours, p.x) for p in calibration.params_a]
        params_b = [(p.k_hours, p.x) for p in calibration.params_b]
        sim_all = _simulate_multi_reach(
            inflow_all[:, 0],
            inflow_all[:, 1],
            outflow_all,
            calibration.thresholds_a,
            calibration.thresholds_b,
            params_a,
            params_b,
            dt_hours,
            calibration.weights["A"],
            calibration.weights["B"],
            calibration.total_gain,
            calibration.baseflow,
            calibration.bias,
        )
    else:
        inflow_mix = weights["A"] * inflow_all[:, 0] + weights["B"] * inflow_all[:, 1]
        sim_all = _simulate_segmented(inflow_mix, outflow_all, calibration.thresholds, params, dt_hours)

    steps = max(12, min(req.forecast_steps, len(aligned)))
    tail = aligned.iloc[-steps:]
    tail_sim = sim_all[-steps:]
    metric_tail = _metrics(tail["C"].values.astype(float), tail_sim)

    return MuskingumForecastResponse(
        success=True,
        model=f"Segmented Muskingum ({calibration.routing_mode})",
        dt_minutes=dt_minutes,
        used_steps=steps,
        metrics={
            "forecast_rmse": metric_tail["rmse"],
            "forecast_nse": metric_tail["nse"],
            "forecast_mape": metric_tail["mape"],
        },
        series={
            "time": [t.isoformat() for t in tail.index.to_pydatetime()],
            "A": [round(float(v), 4) for v in tail["A"].tolist()],
            "B": [round(float(v), 4) for v in tail["B"].tolist()],
            "C_obs": [round(float(v), 4) for v in tail["C"].tolist()],
            "C_forecast": [round(float(v), 4) for v in tail_sim.tolist()],
        },
        full_series={
            "time": [t.isoformat() for t in aligned.index.to_pydatetime()],
            "A": [round(float(v), 4) for v in aligned["A"].tolist()],
            "B": [round(float(v), 4) for v in aligned["B"].tolist()],
            "C_obs": [round(float(v), 4) for v in aligned["C"].tolist()],
            "C_forecast": [round(float(v), 4) for v in sim_all.tolist()],
        },
    )


@app.get("/optimize/health")
async def health():
    return {
        "status": "ok",
        "service": "optimization-api",
        "modules": ["optimize-mock", "muskingum-calibrate", "muskingum-forecast"],
    }


# ---------- 启动入口 ----------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9001, reload=True)
