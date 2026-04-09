package com.flood.alertengine;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * M05 告警引擎微服务入口
 * - 实现四级预警阈值判定
 * - 对接 WebSocket STOMP 推送
 */
@SpringBootApplication
public class AlertEngineApplication {
    public static void main(String[] args) {
        SpringApplication.run(AlertEngineApplication.class, args);
    }
}
