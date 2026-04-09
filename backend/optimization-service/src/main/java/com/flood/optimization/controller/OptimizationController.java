package com.flood.optimization.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 优化调度控制器
 * POST /api/optimize/run  — 触发多目标优化 (Demo返回Mock Pareto前沿)
 * GET  /api/optimize/result — 获取最新优化结果
 */
@RestController
@RequestMapping("/api/optimize")
public class OptimizationController {

    private List<Map<String, Object>> lastResult = new ArrayList<>();

    @PostMapping("/run")
    public ResponseEntity<Map<String, Object>> runOptimize(@RequestBody Map<String, Object> params) {
        // Demo: 生成 20 个 Pareto 解
        List<Map<String, Object>> solutions = new ArrayList<>();
        Random rnd = new Random(42);

        for (int i = 0; i < 20; i++) {
            double floodRisk = 0.05 + (0.35 - 0.05) * i / 19.0 + rnd.nextGaussian() * 0.02;
            double ecoCost = 0.90 - (0.90 - 0.30) * i / 19.0 + rnd.nextGaussian() * 0.03;
            double gate1 = 0.2 + rnd.nextDouble() * 0.6;
            double gate2 = 0.1 + rnd.nextDouble() * 0.7;

            Map<String, Object> sol = new LinkedHashMap<>();
            sol.put("id", i + 1);
            sol.put("floodRisk", Math.round(floodRisk * 1000.0) / 1000.0);
            sol.put("ecologicalCost", Math.round(ecoCost * 1000.0) / 1000.0);
            sol.put("gateOpenings", Map.of("gate1", Math.round(gate1 * 100.0) / 100.0,
                                            "gate2", Math.round(gate2 * 100.0) / 100.0));
            sol.put("recommended", i == 8);
            solutions.add(sol);
        }

        lastResult = solutions;

        return ResponseEntity.ok(Map.of(
            "success", true,
            "solutionCount", solutions.size(),
            "solutions", solutions,
            "algorithm", "NSGA-II (Mock)"
        ));
    }

    @GetMapping("/result")
    public ResponseEntity<Map<String, Object>> getResult() {
        return ResponseEntity.ok(Map.of(
            "solutions", lastResult,
            "count", lastResult.size()
        ));
    }
}
