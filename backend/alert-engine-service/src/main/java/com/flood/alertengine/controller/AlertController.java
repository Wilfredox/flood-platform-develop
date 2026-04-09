package com.flood.alertengine.controller;

import com.flood.alertengine.model.AlertLevel;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.*;

/**
 * 告警判定控制器
 * POST /api/alert/evaluate  — 传入实时数据，返回告警级别
 * GET  /api/alert/active     — 获取当前活跃告警列表
 */
@RestController
@RequestMapping("/api/alert")
public class AlertController {

    /** Demo: 内存存储活跃告警 */
    private final List<Map<String, Object>> activeAlerts = Collections.synchronizedList(new ArrayList<>());

    @PostMapping("/evaluate")
    public ResponseEntity<Map<String, Object>> evaluate(@RequestBody Map<String, Object> payload) {
        String stationId = (String) payload.getOrDefault("stationId", "unknown");
        double waterLevel = ((Number) payload.getOrDefault("waterLevel", 0)).doubleValue();
        double rainfall = ((Number) payload.getOrDefault("rainfall", 0)).doubleValue();

        // Demo 四级阈值判定 (简化)
        AlertLevel level = null;
        if (waterLevel >= 14.0 || rainfall >= 100.0) {
            level = AlertLevel.RED;
        } else if (waterLevel >= 12.0 || rainfall >= 60.0) {
            level = AlertLevel.ORANGE;
        } else if (waterLevel >= 10.0 || rainfall >= 30.0) {
            level = AlertLevel.YELLOW;
        } else if (waterLevel >= 8.0 || rainfall >= 15.0) {
            level = AlertLevel.BLUE;
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("stationId", stationId);
        result.put("waterLevel", waterLevel);
        result.put("rainfall", rainfall);
        result.put("timestamp", Instant.now().toString());

        if (level != null) {
            result.put("alertLevel", level.name());
            result.put("alertLabel", level.getLabel());
            result.put("triggered", true);

            // 加入活跃告警
            Map<String, Object> alertRecord = new LinkedHashMap<>(result);
            activeAlerts.add(alertRecord);
            if (activeAlerts.size() > 200) {
                activeAlerts.subList(0, activeAlerts.size() - 200).clear();
            }
        } else {
            result.put("triggered", false);
        }

        return ResponseEntity.ok(result);
    }

    @GetMapping("/active")
    public ResponseEntity<List<Map<String, Object>>> getActive() {
        return ResponseEntity.ok(new ArrayList<>(activeAlerts));
    }
}
