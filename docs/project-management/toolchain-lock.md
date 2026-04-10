# 工具链锁版规范 · Toolchain Lock

> 生效日期：2026-04-10
> 适用范围：flood-platform 全仓库（frontend / backend / python-services）
> 目标：统一运行时与构建工具版本，避免“同代码不同结果”。

## 1. 冻结版本（不得擅自变更）

| 类别 | 锁定版本 | 说明 |
|------|----------|------|
| Node.js | 20.12.2 | 前端构建与开发统一版本 |
| npm | 10.5.0 | 与 Node 20.12.2 配套 |
| Python | 3.12.11 | Python 服务统一解释器版本 |
| Java（项目要求） | 17（LTS） | 后端 Spring Boot 服务按 `pom.xml` 的 `java.version=17` 执行 |
| Maven | 3.9.13 | Java 服务构建工具 |
| TypeScript（前端） | 5.4.x | 与 `frontend` 当前配置兼容 |
| Vite（前端） | 5.4.x | 与当前构建链路兼容 |

## 2. 必须遵守的规则

1. 未经 Tech Lead 明确批准，不得升级或降级上述版本。
2. 新成员第一次拉起项目前，必须先完成版本核对。
3. CI 环境与本地环境必须保持同一主版本（尤其 Node/Python/Java）。
4. 发现版本漂移时，优先回切到本规范版本，不允许“临时改代码适配本机环境”。

## 3. 本地环境切换命令（Windows）

### 3.1 前端

```bash
cd frontend
nvm use 20.12.2
npm -v
node -v
npm run build
```

### 3.2 Python 服务

```bash
conda activate conda312
python --version
```

### 3.3 Java 服务

```bash
mvn -v
java -version
```

说明：
- 当前仓库 `backend/*/pom.xml` 已固定 `java.version=17`。
- 若本机默认 `java -version` 非 17，请切换 `JAVA_HOME` 到 JDK 17 后再启动后端服务。

## 4. 已知兼容性结论（必须记住）

1. `frontend` 在 Windows 上使用 Node 24 与 Vite 5.4.x，可能出现“无错误栈直接退出”的构建崩溃。
2. 前端构建推荐并已验证稳定组合：Node 20.12.2 + npm 10.5.0。
3. `frontend/tsconfig.json` 已按 TS6 迁移建议移除 `baseUrl`，不再使用 `ignoreDeprecations: "6.0"` 方案。

## 5. 版本变更流程（如确需升级）

1. 提交变更提案（原因、风险、回滚方案）。
2. 在独立分支验证：
   - `frontend npm run build`
   - 至少 1 个 Java 服务可启动
   - 至少 1 个 Python 服务可启动
3. 更新本文件与相关启动文档后，再发起 PR。
4. PR 合并后，全员统一切换，禁止出现混用窗口期。
