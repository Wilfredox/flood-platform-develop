package com.flood.optimization.dto.river1d;

/**
 * River1D 项目草案保存响应 DTO（R10）
 */
public record River1dProjectDraftResponse(
    String projectId,
    String projectName,
    String status,
    Integer riverCount,
    Integer sectionCount,
    Integer structureCount,
    String message
) {}
