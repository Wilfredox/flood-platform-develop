package com.flood.dataingest.controller;

import com.flood.dataingest.model.SensorData;
import com.flood.dataingest.service.SensorDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

/**
 * 传感器数据接入接口
 * POST /api/sensor/data   → 接收传感器数据
 * GET  /api/sensor/latest → 获取最新数据
 */
@RestController
@RequestMapping("/api/sensor")
@CrossOrigin(origins = "*")
public class SensorDataController {

    @Autowired
    private SensorDataService sensorDataService;

    /**
     * 接收传感器上报数据
     * [DEMO-ONLY] 直接存内存，生产版本推送到 Kafka Topic
     */
    @PostMapping("/data")
    public ResponseEntity<?> receiveSensorData(@RequestBody SensorData data) {
        // 简单范围校验
        if (data.getWaterLevel() < 0 || data.getWaterLevel() > 20) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "水位值超出有效范围 (0~20m)",
                "value", data.getWaterLevel()
            ));
        }
        if (data.getRainfall() < 0 || data.getRainfall() > 500) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "雨量值超出有效范围 (0~500mm/h)",
                "value", data.getRainfall()
            ));
        }

        sensorDataService.save(data);
        return ResponseEntity.ok(Map.of("status", "ok", "stationId", data.getStationId()));
    }

    /**
     * 获取站点最新数据
     */
    @GetMapping("/latest")
    public ResponseEntity<?> getLatest(@RequestParam String stationId) {
        Optional<SensorData> data = sensorDataService.getLatest(stationId);
        if (data.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(data.get());
    }
}
