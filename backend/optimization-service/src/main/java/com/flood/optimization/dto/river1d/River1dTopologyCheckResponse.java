package com.flood.optimization.dto.river1d;

import java.util.List;

/**
 * River1D 拓扑检查响应 DTO（R10）
 */
public record River1dTopologyCheckResponse(
    boolean ok,
    Integer riverCount,
    Integer sectionCount,
    Integer nodeCount,
    List<String> issues,
    List<String> warnings
) {}
