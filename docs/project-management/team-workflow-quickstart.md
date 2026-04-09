# 团队协作一页纸（Quick Start）

> 适用仓库：flood-platform
> 目标：让团队成员用同一套流程开发、评审、发布，减少返工。

## 1. 角色与职责

- Tech Lead：分解任务、审核 PR、控制 `main` 发布。
- 开发成员：在功能分支开发，提交 PR 到 `develop`。
- 测试/验收：按清单验证功能，反馈缺陷并回归。

## 2. 分支规则（必须遵守）

- 稳定发布：`main`
- 日常集成：`develop`
- 功能开发：`feature/<模块-描述>`
- 缺陷修复：`fix/<问题-描述>`
- 紧急修复：`hotfix/<问题-描述>`（仅线上问题）
- 发布准备：`release/vX.Y.Z`

约束：
- 不允许直接向 `main` 提交代码。
- 所有改动必须通过 PR 合并。

## 3. 提交规范

格式：`<type>(<scope>): <description>`

常用 type：
- `feat`：新功能
- `fix`：缺陷修复
- `docs`：文档变更
- `refactor`：重构
- `test`：测试
- `chore`：工程维护

示例：
- `feat(M01): add basin boundary overlay on map`
- `fix(M09): repair agent chat scroll clipping`

## 4. 每日协作流程（10 分钟对齐版）

1. 开始前同步：
   - `git checkout develop`
   - `git pull`
2. 创建任务分支：
   - `git checkout -b feature/Mxx-xxx`
3. 开发与自测：
   - 小步提交，至少保证本地可运行。
4. 提交与推送：
   - `git add -A`
   - `git commit -m "feat(Mxx): ..."`
   - `git push -u origin feature/Mxx-xxx`
5. 发起 PR：
   - 目标分支：`develop`
   - 填写变更说明、影响范围、验证结果。
6. 评审后处理：
   - 根据评论修复后继续 push 到同一分支。

## 5. PR 最小模板（复制即用）

### 变更内容
- 本 PR 做了什么（3-5 条）

### 影响范围
- frontend/backend/python-services/docs（按实际勾选）

### 验证结果
- 本地运行结果
- 核心截图/日志（如有）

### 风险与回滚
- 可能风险
- 回滚方式（回退提交或 revert PR）

## 6. 发布与版本

- 日常合并：`feature/*` -> `develop`
- 发布前：`develop` -> `release/vX.Y.Z`
- 验收通过：`release/*` -> `main`，打 tag（如 `v0.1.0-demo`）
- 紧急修复：`hotfix/*` 同步回 `main` 与 `develop`

## 7. 合并门禁（建议）

- 至少 1 名 Reviewer 通过
- CI 通过（如已接入）
- 自检清单完成
- 无冲突、无明显回归

## 8. 常见错误（避免）

- 在 `main` 上直接开发
- 一个 PR 混入多个不相关需求
- 提交信息无语义（如“update code”）
- 未自测就提 PR

## 9. 配套文档索引

- 分支策略：`docs/project-management/git-branch-strategy.md`
- 协作规范：`docs/flood_platform_prompt_system.md`
- 模块自检：`docs/project-management/module-checklist-template.md`
- 开发记录：`docs/project-management/dev-log.md`
