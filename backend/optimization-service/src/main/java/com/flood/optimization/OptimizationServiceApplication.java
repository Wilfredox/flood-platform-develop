package com.flood.optimization;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * M06 优化调度微服务入口
 * - 代理转发请求至 Python NSGA-II 服务
 * - 管理调度方案存储
 */
@SpringBootApplication
public class OptimizationServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OptimizationServiceApplication.class, args);
    }
}
