package com.flood.optimization.dto.river1d;

import java.util.List;

/**
 * River1D 项目草案保存请求 DTO（R10）
 */
public record River1dProjectDraftRequest(
    String projectName,
    String crs,
    String description,
    List<LineFeatureDto> rivers,
    List<LineFeatureDto> banks,
    List<SectionFeatureDto> sections,
    List<LineFeatureDto> structures,
    List<NodeFeatureDto> nodes
) {
    public record LineFeatureDto(
        String id,
        String name,
        List<PointDto> coords
    ) {}

    public record SectionFeatureDto(
        String id,
        String name,
        Double station,
        List<PointDto> coords,
        List<SectionProfilePointDto> profile
    ) {}

    public record NodeFeatureDto(
        String id,
        Double lat,
        Double lng,
        String nodeType
    ) {}

    public record PointDto(
        Double lat,
        Double lng
    ) {}

    public record SectionProfilePointDto(
        Double dist,
        Double elev
    ) {}
}
