package com.flood.optimization.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 分段马斯金根法代理控制器
 *
 * 作用：
 * 1. 对前端暴露统一的 Java API 入口（8084）
 * 2. 代理转发至 Python optimization-api（9001）
 */
@RestController
@RequestMapping("/api/hydrology/muskingum")
@CrossOrigin(origins = "*")
public class MuskingumController {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${services.python.optimization-api-base-url:http://localhost:9001}")
    private String pythonBaseUrl;

    @PostMapping("/calibrate")
    public ResponseEntity<?> calibrate(@RequestBody Map<String, Object> requestBody) {
        return forward("/hydrology/muskingum/calibrate", requestBody);
    }

    @PostMapping("/forecast")
    public ResponseEntity<?> forecast(@RequestBody Map<String, Object> requestBody) {
        return forward("/hydrology/muskingum/forecast", requestBody);
    }

    @GetMapping("/health")
    public ResponseEntity<?> health() {
        String url = pythonBaseUrl + "/optimize/health";
        try {
            Map<?, ?> response = restTemplate.getForObject(url, Map.class);
            return ResponseEntity.ok(response);
        } catch (HttpStatusCodeException ex) {
            return ResponseEntity.status(ex.getStatusCode()).body(parseErrorBody(ex.getResponseBodyAsString(), ex.getStatusCode().value()));
        } catch (RestClientException ex) {
            return ResponseEntity.status(502).body(Map.of(
                "message", "无法连接 Python 马斯金根服务",
                "pythonBaseUrl", pythonBaseUrl,
                "error", ex.getMessage()
            ));
        }
    }

    private ResponseEntity<?> forward(String path, Map<String, Object> payload) {
        String url = pythonBaseUrl + path;
        try {
            Map<?, ?> response = restTemplate.postForObject(url, payload, Map.class);
            return ResponseEntity.ok(response);
        } catch (HttpStatusCodeException ex) {
            return ResponseEntity.status(ex.getStatusCode()).body(parseErrorBody(ex.getResponseBodyAsString(), ex.getStatusCode().value()));
        } catch (RestClientException ex) {
            return ResponseEntity.status(502).body(Map.of(
                "message", "无法连接 Python 马斯金根服务",
                "pythonBaseUrl", pythonBaseUrl,
                "error", ex.getMessage()
            ));
        }
    }

    private Map<String, Object> parseErrorBody(String raw, int status) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("status", status);
        body.put("message", "Python 服务返回错误");
        body.put("detail", raw == null || raw.isBlank() ? "(empty)" : raw);
        return body;
    }
}
