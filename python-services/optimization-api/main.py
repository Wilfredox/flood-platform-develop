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


class MuskingumCalibrateRequest(BaseModel):
    dataset: MuskingumDatasetConfig = Field(default_factory=MuskingumDatasetConfig)
    dt_minutes: int = 60
    train_ratio: float = 0.7
    segments: int = 3
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

    weights, thresholds, params, sim_train = _optimize_segmented(
        inflow_train,
        outflow_train,
        dt_hours,
        req.segments,
        req.iterations,
        req.seed,
    )

    inflow_mix_all = weights["A"] * inflow_all[:, 0] + weights["B"] * inflow_all[:, 1]
    sim_all = _simulate_segmented(inflow_mix_all, outflow_all, thresholds, params, dt_hours)

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
    )
    LAST_CALIBRATION = calibration

    keep = max(60, min(req.include_series_points, sample_count))
    tail = aligned.iloc[-keep:]
    tail_sim = sim_all[-keep:]

    return MuskingumCalibrateResponse(
        success=True,
        algorithm="Segmented Muskingum + Random Search",
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
    inflow_mix = weights["A"] * inflow_all[:, 0] + weights["B"] * inflow_all[:, 1]
    sim_all = _simulate_segmented(inflow_mix, outflow_all, calibration.thresholds, params, dt_hours)

    steps = max(12, min(req.forecast_steps, len(aligned)))
    tail = aligned.iloc[-steps:]
    tail_sim = sim_all[-steps:]
    metric_tail = _metrics(tail["C"].values.astype(float), tail_sim)

    return MuskingumForecastResponse(
        success=True,
        model="Segmented Muskingum",
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
