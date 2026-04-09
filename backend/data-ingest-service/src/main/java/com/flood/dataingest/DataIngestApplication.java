package com.flood.dataingest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * M04 数据接入与预处理服务
 * [DEMO-ONLY] 简化版：HTTP 接口接收 Mock 传感器数据
 * 生产版本将接入 MQTT/Kafka 真实数据管道
 */
@SpringBootApplication
public class DataIngestApplication {
    public static void main(String[] args) {
        SpringApplication.run(DataIngestApplication.class, args);
    }
}
