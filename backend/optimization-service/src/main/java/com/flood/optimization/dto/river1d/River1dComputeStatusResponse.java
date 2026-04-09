package com.flood.optimization.dto.river1d;

import java.util.List;

/**
 * River1D 计算任务状态响应 DTO（R11）
 */
public record River1dComputeStatusResponse(
    String taskId,
    String projectId,
    String status,
    Integer progress,
    String stage,
    List<String> logs,
    String startedAt,
    String finishedAt
) {}
