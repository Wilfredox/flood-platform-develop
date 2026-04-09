package com.flood.optimization.dto.river1d;

/**
 * River1D 拓扑检查请求 DTO（R10）
 */
public record River1dTopologyCheckRequest(
    String projectId,
    River1dProjectDraftRequest project
) {}
