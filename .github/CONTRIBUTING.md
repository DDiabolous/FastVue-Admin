# FastVue-Admin 贡献指南

感谢关注并参与 FastVue-Admin 的开发与维护！开源社区的持续演进离不开每位开发者的贡献。无论是修复缺陷、改进文档、编写自动化测试，还是提出新功能建议，我们都十分欢迎。

在提交代码前，请花几分钟阅读以下规范与工作流程。

---

## 1. 行为准则与约定

- 保持友好与包容的交流环境。
- 遵循单一职责原则：一个 Pull Request 尽量只关注一个特定问题或特性。
- 代码必须附带相应的自动化测试，确保新功能或缺陷修复具备长久回归保障。

---

## 2. 本地开发与测试流程

### 前端开发
1. 进入前端目录：
   ```bash
   cd frontend
   npm ci
   ```
2. 启动开发模式：
   - 精简版开发：`npm run dev`
   - 完整版开发：`npm run dev:full`
3. 提交前必须通过测试与两种构建：
   ```bash
   npm test
   npm run build
   npm run build:full
   ```

### 后端开发
1. 进入后端目录：
   ```bash
   cd backend
   uv sync --all-groups
   ```
2. 代码格式与风格检查：
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```
3. 数据库迁移与集成测试：
   需提供专门的测试数据库并配置环境变量（测试运行时会在独立 schema 中隔离执行，并在结束后清理）：
   ```bash
   TEST_DATABASE_URL="postgresql+asyncpg://<user>:<password>@localhost:5432/<dbname>" uv run pytest
   ```

---

## 3. Git 分支与提交规范

### 分支命名
- 特性分支：`feat/short-description`
- 缺陷修复：`fix/short-description`
- 文档优化：`docs/short-description`
- 性能/重构：`refactor/short-description`

### Commit Message 规范
遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```text
<type>(<scope>): <subject>

[optional body]
```

常用 `type` 类型：
- `feat`: 新增业务功能或组件
- `fix`: 修复缺陷或安全问题
- `docs`: 文档变更或示例说明补充
- `style`: 不影响代码逻辑的代码格式变动
- `refactor`: 代码重构（既不修复 bug 也不添加功能）
- `test`: 增加或修正自动化测试
- `chore`: 构建系统、依赖更新或 CI 配置变更

---

## 4. Pull Request 流程

1. **Fork 本仓库** 并基于 `main` 分支切出您的开发分支。
2. **编写代码并完成本地自测**：
   - 前端：`npm test`、`npm run build`、`npm run build:full`。
   - 后端：`ruff check`、`ruff format`、PostgreSQL 集成测试。
3. **提交 PR**：
   - 准确填写 PR 模板中的各项检查，关联相关的 Issue。
   - 涉及前端 UI/UX 的调整，**必须附上亮色模式、暗色模式或移动端的相关截图/录屏**。
4. **等待 CI 流水线通过并参与 Code Review**。
