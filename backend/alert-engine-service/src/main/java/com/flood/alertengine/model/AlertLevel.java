package com.flood.alertengine.model;

/**
 * 告警级别枚举 — 蓝/黄/橙/红
 */
public enum AlertLevel {
    BLUE(1, "蓝色"),
    YELLOW(2, "黄色"),
    ORANGE(3, "橙色"),
    RED(4, "红色");

    private final int code;
    private final String label;

    AlertLevel(int code, String label) {
        this.code = code;
        this.label = label;
    }

    public int getCode() { return code; }
    public String getLabel() { return label; }
}
