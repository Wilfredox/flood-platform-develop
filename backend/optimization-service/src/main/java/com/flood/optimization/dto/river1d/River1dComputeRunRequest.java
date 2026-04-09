package com.flood.optimization.dto.river1d;

import java.util.Map;

/**
 * River1D 计算任务启动请求 DTO（R11）
 */
public record River1dComputeRunRequest(
    String projectId,
    River1dProjectDraftRequest project,
    Map<String, Object> params
) {}
