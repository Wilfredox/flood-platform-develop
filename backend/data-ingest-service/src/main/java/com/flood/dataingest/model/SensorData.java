package com.flood.dataingest.model;

import java.time.Instant;

/**
 * 传感器数据模型
 */
public class SensorData {
    private String stationId;
    private String stationName;
    private double waterLevel;    // 水位 (m)
    private double rainfall;      // 雨量 (mm/h)
    private double flow;          // 流量 (m³/s)
    private Instant timestamp;

    // Getters & Setters
    public String getStationId() { return stationId; }
    public void setStationId(String stationId) { this.stationId = stationId; }

    public String getStationName() { return stationName; }
    public void setStationName(String stationName) { this.stationName = stationName; }

    public double getWaterLevel() { return waterLevel; }
    public void setWaterLevel(double waterLevel) { this.waterLevel = waterLevel; }

    public double getRainfall() { return rainfall; }
    public void setRainfall(double rainfall) { this.rainfall = rainfall; }

    public double getFlow() { return flow; }
    public void setFlow(double flow) { this.flow = flow; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }
}
