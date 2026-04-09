"""
M07 Python ML 洪水预报 API
FastAPI 服务 — 端口 9002
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random
import math

app = FastAPI(
    title="洪水预报服务",
    description="基于 LSTM / Transformer 的洪水水位预报 (Demo 使用线性外推)",
    version="0.1.0-demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 数据模型 ----------

class ForecastRequest(BaseModel):
    station_id: str = "ST001"
    history_hours: int = 24
    forecast_hours: int = 6
    current_water_level: float = 8.5
    current_rainfall: float = 15.0


class ForecastPoint(BaseModel):
    hour_offset: int
    water_level: float
    confidence_lower: float
    confidence_upper: float
    rainfall_predicted: float


class ForecastResponse(BaseModel):
    success: bool
    model: str
    station_id: str
    forecast_hours: int
    points: List[ForecastPoint]
    peak_level: float
    peak_hour: int
    alert_level: str  # NONE / BLUE / YELLOW / ORANGE / RED


# ---------- 路由 ----------

@app.post("/forecast/run", response_model=ForecastResponse)
async def run_forecast(req: ForecastRequest):
    """
    运行水位预报 (Demo 使用正弦+线性外推模拟)
    正式版将加载 ONNX/TorchScript 模型
    """
    random.seed(hash(req.station_id) % 10000)
    points: List[ForecastPoint] = []

    base = req.current_water_level
    rain = req.current_rainfall
    peak_level = base
    peak_hour = 0

    for h in range(1, req.forecast_hours + 1):
        # 模拟涨水趋势: 抛物线 + 随机扰动
        trend = rain * 0.02 * h - 0.003 * h * h
        noise = random.gauss(0, 0.1)
        wl = round(base + trend + noise, 2)
        conf_range = 0.2 + 0.08 * h
        rainfall_pred = round(max(0, rain - h * 1.5 + random.gauss(0, 2)), 1)

        points.append(ForecastPoint(
            hour_offset=h,
            water_level=wl,
            confidence_lower=round(wl - conf_range, 2),
            confidence_upper=round(wl + conf_range, 2),
            rainfall_predicted=rainfall_pred,
        ))

        if wl > peak_level:
            peak_level = wl
            peak_hour = h

    # 判定预警级别
    if peak_level >= 14.0:
        alert = "RED"
    elif peak_level >= 12.0:
        alert = "ORANGE"
    elif peak_level >= 10.0:
        alert = "YELLOW"
    elif peak_level >= 8.0:
        alert = "BLUE"
    else:
        alert = "NONE"

    return ForecastResponse(
        success=True,
        model="Linear-Extrapolation (Mock)",
        station_id=req.station_id,
        forecast_hours=req.forecast_hours,
        points=points,
        peak_level=peak_level,
        peak_hour=peak_hour,
        alert_level=alert,
    )


@app.get("/forecast/health")
async def health():
    return {"status": "ok", "service": "ml-forecast-api"}


# ---------- 启动入口 ----------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9002, reload=True)
