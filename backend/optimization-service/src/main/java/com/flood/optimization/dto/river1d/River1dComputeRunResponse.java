package com.flood.optimization.dto.river1d;

/**
 * River1D 计算任务启动响应 DTO（R11）
 */
public record River1dComputeRunResponse(
    String taskId,
    String projectId,
    String status,
    String message
) {}
