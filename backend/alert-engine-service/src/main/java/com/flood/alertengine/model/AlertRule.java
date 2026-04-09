package com.flood.alertengine.model;

/**
 * 告警阈值配置规则
 */
public class AlertRule {
    private String stationId;
    private AlertLevel level;
    private double waterLevelThreshold;  // 水位阈值 (m)
    private double rainfallThreshold;    // 雨量阈值 (mm/h)
    private double flowThreshold;        // 流量阈值 (m³/s)

    public String getStationId() { return stationId; }
    public void setStationId(String stationId) { this.stationId = stationId; }

    public AlertLevel getLevel() { return level; }
    public void setLevel(AlertLevel level) { this.level = level; }

    public double getWaterLevelThreshold() { return waterLevelThreshold; }
    public void setWaterLevelThreshold(double waterLevelThreshold) { this.waterLevelThreshold = waterLevelThreshold; }

    public double getRainfallThreshold() { return rainfallThreshold; }
    public void setRainfallThreshold(double rainfallThreshold) { this.rainfallThreshold = rainfallThreshold; }

    public double getFlowThreshold() { return flowThreshold; }
    public void setFlowThreshold(double flowThreshold) { this.flowThreshold = flowThreshold; }
}
