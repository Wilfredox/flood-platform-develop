# Git 分支管理策略 · Branch Strategy

> 基于 Git Flow 变体，适配本项目五阶段路线图。

---

## 分支模型

```
main          ●───────────●──────────────●──────── (稳定发布)
               \         ↑              ↑
develop         ●───●───●───●───●───●───●──────── (开发主线)
                 \     / \     /
feature/*         ●──●    ●──●                     (功能分支)
                           \
hotfix/*                    ●──●                   (紧急修复)
release/*                        ●──●              (发布准备)
```

---

## 分支说明

| 分支 | 命名规则 | 来源 | 合并目标 | 说明 |
|------|---------|------|---------|------|
| `main` | 固定 | - | - | 稳定发布分支，每个版本对应一个 tag |
| `develop` | 固定 | main | main | 开发主线，日常集成分支 |
| `feature/*` | `feature/模块-描述` | develop | develop | 新功能开发 |
| `hotfix/*` | `hotfix/问题描述` | main | main + develop | 紧急线上修复 |
| `release/*` | `release/vX.Y.Z` | develop | main + develop | 发布前测试与修复 |

---

## 功能分支命名规范

按本项目模块编号命名，清晰追溯：

```
feature/M04-kafka-data-ingest       # M04 数据接入真实 Kafka
feature/M05-alert-threshold-logic   # M05 告警引擎阈值逻辑
feature/M06-nsga2-optimization      # M06 NSGA-II 优化实现
feature/M07-lstm-forecast           # M07 LSTM 预报模型
feature/M10-jwt-spring-security     # M10 真实 JWT 认证
feature/frontend-websocket          # 前端 WebSocket 接入
feature/docker-k8s-deploy           # 容器化部署
```

---

## 版本标签规范

遵循 [语义化版本 SemVer](https://semver.org/lang/zh-CN/)：

```
vMAJOR.MINOR.PATCH[-预发布标识]

v0.1.0-demo    ← 当前 (Demo 阶段完成)
v0.2.0-alpha   ← Phase-2 (真实数据流)
v0.3.0-alpha   ← Phase-3 (ML 模型)
v0.4.0-beta    ← Phase-4 (Cesium 数字孪生)
v1.0.0         ← Phase-5 (生产就绪)
```

---

## 工作流程

### 1. 开发新功能

```bash
# 从 develop 创建功能分支
git checkout develop
git pull
git checkout -b feature/M04-kafka-data-ingest

# 开发 & 提交
git add -A
git commit -m "feat(M04): 接入 Kafka consumer 消费水文数据"

# 完成后合并回 develop
git checkout develop
git merge --no-ff feature/M04-kafka-data-ingest
git branch -d feature/M04-kafka-data-ingest
```

### 2. 准备发布

```bash
git checkout develop
git checkout -b release/v0.2.0

# 修复发布前问题 ...
git commit -m "fix: 修复告警阈值边界条件"

# 合并到 main 并打 tag
git checkout main
git merge --no-ff release/v0.2.0
git tag -a v0.2.0-alpha -m "Phase-2: 真实数据流接入"

# 合并回 develop
git checkout develop
git merge --no-ff release/v0.2.0
git branch -d release/v0.2.0
```

### 3. 紧急修复

```bash
git checkout main
git checkout -b hotfix/fix-alert-crash

git commit -m "fix: 修复告警空指针崩溃"

git checkout main
git merge --no-ff hotfix/fix-alert-crash
git tag -a v0.1.1-demo -m "Hotfix: 告警崩溃修复"

git checkout develop
git merge --no-ff hotfix/fix-alert-crash
git branch -d hotfix/fix-alert-crash
```

---

## Commit Message 规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(M01): 添加大屏站点筛选功能` |
| `fix` | 修复 Bug | `fix(M05): 修复告警级别判定逻辑` |
| `docs` | 文档变更 | `docs: 更新 README 部署说明` |
| `style` | 代码格式 | `style: 统一缩进为 2 空格` |
| `refactor` | 重构 | `refactor(M04): 提取数据清洗公共方法` |
| `perf` | 性能优化 | `perf(M07): 优化预报模型推理速度` |
| `test` | 测试 | `test(M06): 添加空间优化单元测试` |
| `chore` | 工程化 | `chore: 升级 Spring Boot 到 3.2.5` |
| `ci` | CI/CD | `ci: 添加 GitHub Actions 构建流水线` |
| `init` | 初始化 | `init: 项目初始化首次提交` |

### Scope 范围（可选）

使用模块编号：`M01` ~ `M11`，或 `frontend` / `backend` / `docker` / `docs`

---

## 当前分支状态

```
main      ← 稳定发布 (v0.1.0-demo)
develop   ← 开发主线 (当前工作分支)
```

---

> 💡 **提示：** 日常开发在 `develop` 或 `feature/*` 上进行，永远不要直接在 `main` 上提交代码。
