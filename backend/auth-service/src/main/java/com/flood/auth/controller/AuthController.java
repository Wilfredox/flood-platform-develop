package com.flood.auth.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 认证控制器
 * POST /auth/login — 账号密码登录，返回 Mock JWT
 * GET  /auth/me    — 获取当前用户信息
 */
@RestController
@RequestMapping("/auth")
public class AuthController {

    /** Demo 内置用户 */
    private static final Map<String, Map<String, String>> USERS = new LinkedHashMap<>();

    static {
        USERS.put("admin",    Map.of("password", "admin123",  "role", "admin",    "name", "系统管理员"));
        USERS.put("province", Map.of("password", "p123",      "role", "province", "name", "省级用户"));
        USERS.put("city",     Map.of("password", "c123",      "role", "city",     "name", "市级用户"));
        USERS.put("county",   Map.of("password", "co123",     "role", "county",   "name", "县级用户"));
        USERS.put("viewer",   Map.of("password", "v123",      "role", "viewer",   "name", "只读用户"));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        String username = body.getOrDefault("username", "");
        String password = body.getOrDefault("password", "");

        Map<String, String> user = USERS.get(username);
        if (user == null || !user.get("password").equals(password)) {
            return ResponseEntity.status(401).body(Map.of(
                "success", false,
                "message", "用户名或密码错误"
            ));
        }

        // Mock JWT
        String token = "mock-jwt-" + username + "-" + UUID.randomUUID().toString().substring(0, 8);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("success", true);
        result.put("token", token);
        result.put("user", Map.of(
            "username", username,
            "name", user.get("name"),
            "role", user.get("role")
        ));

        return ResponseEntity.ok(result);
    }

    @GetMapping("/me")
    public ResponseEntity<Map<String, Object>> me(@RequestHeader(value = "Authorization", defaultValue = "") String auth) {
        // Demo 简化: 从 token 中解析 username
        if (auth.startsWith("Bearer mock-jwt-")) {
            String tokenBody = auth.replace("Bearer mock-jwt-", "");
            String username = tokenBody.split("-")[0];
            Map<String, String> user = USERS.get(username);
            if (user != null) {
                return ResponseEntity.ok(Map.of(
                    "username", username,
                    "name", user.get("name"),
                    "role", user.get("role")
                ));
            }
        }
        return ResponseEntity.status(401).body(Map.of("message", "未授权"));
    }
}
