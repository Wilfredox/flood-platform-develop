# 模块自检清单模板 · Module Checklist

> 每个模块完成后填写此清单，用于 PR Review 和领导审阅。

---

## 通用自检项（所有模块必须满足）

- [ ] 页面/接口可正常运行，无控制台 Error
- [ ] 核心交互流程可完整走通（点击 → 响应 → 数据展示）
- [ ] 已推送到对应的 feature 分支
- [ ] Commit Message 符合规范：`[类型](模块): 描述`
- [ ] 关键逻辑已添加代码注释
- [ ] Demo 简化部分已标注 `[DEMO-ONLY]` 注释
- [ ] Mock 数据结构已记录在 `docs/api/` 中
- [ ] 不影响其他已完成模块

---

## 前端模块专项检查

- [ ] TypeScript 零报错
- [ ] Element Plus 组件正确使用
- [ ] 暗色主题风格统一（色值取自 style-guide）
- [ ] 布局在 1920×1080 分辨率下正确显示
- [ ] ECharts 图表主题配置统一

## 后端模块专项检查

- [ ] API 接口可通过 curl/Postman 正常调用
- [ ] 返回 JSON 格式与接口契约一致
- [ ] 错误码规范（200/400/401/403/500）
- [ ] application.yml 配置有注释说明

## Python 服务专项检查

- [ ] FastAPI 文档页面 (/docs) 可正常访问
- [ ] requirements.txt 已更新
- [ ] 数据格式与 Spring Boot 调用端一致
