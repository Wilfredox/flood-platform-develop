package com.flood.dataingest.service;

import com.flood.dataingest.model.SensorData;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 传感器数据服务 (Demo 阶段使用内存存储)
 */
@Service
public class SensorDataService {

    /** stationId -> 最新数据 */
    private final Map<String, SensorData> latestCache = new ConcurrentHashMap<>();

    /** stationId -> 历史列表(最多保留 1000 条) */
    private final Map<String, List<SensorData>> historyCache = new ConcurrentHashMap<>();

    /**
     * 保存一条传感器数据
     */
    public void save(SensorData data) {
        if (data.getTimestamp() == null) {
            data.setTimestamp(Instant.now());
        }
        latestCache.put(data.getStationId(), data);
        historyCache.computeIfAbsent(data.getStationId(), k -> Collections.synchronizedList(new ArrayList<>()));
        List<SensorData> history = historyCache.get(data.getStationId());
        history.add(data);
        // 仅保留最近 1000 条
        if (history.size() > 1000) {
            history.subList(0, history.size() - 1000).clear();
        }
    }

    /**
     * 获取指定站点最新数据
     */
    public Optional<SensorData> getLatest(String stationId) {
        return Optional.ofNullable(latestCache.get(stationId));
    }

    /**
     * 获取所有站点最新数据
     */
    public Collection<SensorData> getAllLatest() {
        return latestCache.values();
    }
}
