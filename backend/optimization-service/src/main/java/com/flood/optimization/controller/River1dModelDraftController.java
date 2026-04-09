package com.flood.optimization.controller;

import com.flood.optimization.dto.river1d.River1dProjectDraftRequest;
import com.flood.optimization.dto.river1d.River1dProjectDraftResponse;
import com.flood.optimization.dto.river1d.River1dComputeRunRequest;
import com.flood.optimization.dto.river1d.River1dComputeRunResponse;
import com.flood.optimization.dto.river1d.River1dComputeStatusResponse;
import com.flood.optimization.dto.river1d.River1dTopologyCheckRequest;
import com.flood.optimization.dto.river1d.River1dTopologyCheckResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * River1D 模型数据接口草案（R10）
 *
 * 说明：
 * 1. 当前为 Draft 版本，使用内存存储，不落库。
 * 2. 目标是先固化前后端数据契约，后续再替换为真实 service + repository。
 */
@RestController
@RequestMapping("/api/river1d/projects")
@CrossOrigin(origins = "*")
public class River1dModelDraftController {

    private final Map<String, River1dProjectDraftRequest> draftStore = new ConcurrentHashMap<>();
    private final Map<String, ComputeTask> computeTaskStore = new ConcurrentHashMap<>();

    private static final int MOCK_COMPUTE_DURATION_SECONDS = 24;

    private record ComputeTask(
        String taskId,
        String projectId,
        long startedAtMs
    ) {}

    @PostMapping("/draft")
    public ResponseEntity<River1dProjectDraftResponse> saveDraft(@RequestBody River1dProjectDraftRequest request) {
        String projectId = UUID.randomUUID().toString();
        draftStore.put(projectId, request);

        int riverCount = sizeOf(request.rivers());
        int sectionCount = sizeOf(request.sections());
        int structureCount = sizeOf(request.structures());

        return ResponseEntity.ok(new River1dProjectDraftResponse(
            projectId,
            request.projectName(),
            "DRAFT_SAVED",
            riverCount,
            sectionCount,
            structureCount,
            "River1D 草案保存成功"
        ));
    }

    @GetMapping("/draft/{projectId}")
    public ResponseEntity<Map<String, Object>> getDraft(@PathVariable String projectId) {
        River1dProjectDraftRequest project = draftStore.get(projectId);
        if (project == null) {
            return ResponseEntity.notFound().build();
        }

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("projectId", projectId);
        body.put("project", project);
        body.put("status", "DRAFT_LOADED");
        return ResponseEntity.ok(body);
    }

    @PostMapping("/topology/check")
    public ResponseEntity<River1dTopologyCheckResponse> checkTopology(@RequestBody River1dTopologyCheckRequest request) {
        River1dProjectDraftRequest project = request.project();
        if (project == null && request.projectId() != null) {
            project = draftStore.get(request.projectId());
        }
        if (project == null) {
            return ResponseEntity.badRequest().body(new River1dTopologyCheckResponse(
                false,
                0,
                0,
                0,
                List.of("缺少 project 数据或 projectId 无效"),
                List.of()
            ));
        }

        List<String> issues = new ArrayList<>();
        List<String> warnings = new ArrayList<>();

        int riverCount = sizeOf(project.rivers());
        int sectionCount = sizeOf(project.sections());
        int nodeCount = sizeOf(project.nodes());

        if (riverCount == 0) {
            issues.add("未发现河道数据，无法进行有效拓扑检查");
        }
        if (sectionCount > 0 && riverCount == 0) {
            warnings.add("存在断面数据但无河道，断面里程与归属关系无法校核");
        }
        if (nodeCount == 0 && riverCount > 0) {
            warnings.add("未提供节点数据，建议先执行前端节点生成后再提交");
        }

        // 断面 profile 基础校验
        if (project.sections() != null) {
            project.sections().forEach(section -> {
                if (section.profile() == null || section.profile().size() < 2) {
                    warnings.add("断面 " + safeName(section.name(), section.id()) + " 的 profile 点不足 2 个");
                }
            });
        }

        boolean ok = issues.isEmpty();
        return ResponseEntity.ok(new River1dTopologyCheckResponse(
            ok,
            riverCount,
            sectionCount,
            nodeCount,
            issues,
            warnings
        ));
    }

    @PostMapping("/compute/run")
    public ResponseEntity<?> runCompute(@RequestBody River1dComputeRunRequest request) {
        String projectId = request.projectId();
        River1dProjectDraftRequest project = request.project();

        if (isBlank(projectId) && project == null) {
            return ResponseEntity.badRequest().body(Map.of(
                "message", "缺少 projectId 或 project 数据，无法启动计算"
            ));
        }

        if (project != null) {
            if (isBlank(projectId)) {
                projectId = UUID.randomUUID().toString();
            }
            draftStore.put(projectId, project);
        } else if (!draftStore.containsKey(projectId)) {
            return ResponseEntity.badRequest().body(Map.of(
                "message", "projectId 无效，未找到已保存草案"
            ));
        }

        String taskId = UUID.randomUUID().toString();
        computeTaskStore.put(taskId, new ComputeTask(taskId, projectId, System.currentTimeMillis()));

        return ResponseEntity.ok(new River1dComputeRunResponse(
            taskId,
            projectId,
            "RUNNING",
            "River1D 计算任务已启动（Mock）"
        ));
    }

    @GetMapping("/compute/{taskId}/status")
    public ResponseEntity<?> getComputeStatus(@PathVariable String taskId) {
        ComputeTask task = computeTaskStore.get(taskId);
        if (task == null) {
            return ResponseEntity.notFound().build();
        }

        long now = System.currentTimeMillis();
        long elapsedMs = Math.max(0L, now - task.startedAtMs());
        int progress = (int) Math.min(100, (elapsedMs * 100) / (MOCK_COMPUTE_DURATION_SECONDS * 1000L));
        String stage = resolveStage(progress);
        String status = progress >= 100 ? "SUCCEEDED" : "RUNNING";
        String startedAt = String.valueOf(task.startedAtMs());
        String finishedAt = progress >= 100 ? String.valueOf(task.startedAtMs() + MOCK_COMPUTE_DURATION_SECONDS * 1000L) : null;

        return ResponseEntity.ok(new River1dComputeStatusResponse(
            task.taskId(),
            task.projectId(),
            status,
            progress,
            stage,
            buildMockLogs(progress),
            startedAt,
            finishedAt
        ));
    }

    private int sizeOf(List<?> list) {
        return list == null ? 0 : list.size();
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private String resolveStage(int progress) {
        if (progress < 20) {
            return "加载基础数据";
        }
        if (progress < 45) {
            return "构建河网拓扑";
        }
        if (progress < 70) {
            return "组装断面与边界条件";
        }
        if (progress < 95) {
            return "执行水动力求解";
        }
        return "汇总结果与报告";
    }

    private List<String> buildMockLogs(int progress) {
        List<String> logs = new ArrayList<>();
        logs.add("[INFO] 任务已创建，开始校验输入数据...");
        if (progress >= 10) {
            logs.add("[INFO] 网格与河道节点加载完成");
        }
        if (progress >= 35) {
            logs.add("[INFO] 拓扑关系检查通过，未发现致命错误");
        }
        if (progress >= 55) {
            logs.add("[INFO] 断面 profile 与糙率参数装载完成");
        }
        if (progress >= 75) {
            logs.add("[INFO] 水动力迭代进行中，当前已收敛至阈值以内");
        }
        if (progress >= 100) {
            logs.add("[SUCCESS] 计算完成，结果文件已生成（Mock）");
        }
        return logs;
    }

    private String safeName(String name, String fallback) {
        if (name != null && !name.isBlank()) {
            return name;
        }
        return fallback == null ? "(unknown)" : fallback;
    }
}
