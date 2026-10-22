# 更新日志 (Changelog)

本项目遵循 [Semantic Versioning (语义化版本 2.0.0)](https://semver.org/lang/zh-CN/) 规范。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## [Unreleased] - 开发中

### 新增 (Added)
- 新增 GitHub Actions CI 持续集成工作流，覆盖前端测试、Starter/Full 双模式构建、后端 Ruff 校验、Alembic 迁移一致性检测、PostgreSQL 集成测试及 Docker Compose 容器健康度验证。
- 建立开源社区规范基础设施：贡献指南 (`CONTRIBUTING.md`)、安全策略 (`SECURITY.md`)、PR 模板与 Issue 表单模板。

---

## [1.0.0] - 2026-10-21

### 新增 (Added)
- **前端架构**：
  - 基于 Vue 3、Pinia、Element Plus、Vite 构建。
  - 支持 Starter（精简起步）与 Full（完整业务演示）两种模式。
  - 提供无闪烁主题切换（圆形扩散动画、亮暗色模式、表格紧凑度调节）。
  - 内置全局 `⌘/Ctrl + K` 快速指令搜索与页面收藏、最近访问历史。
  - 封装统一的后台页面布局组件（`PageContainer`、`FilterPanel`、`StatisticCard` 等）。
  - 灵活的数据接入层，支持无依赖的浏览器 Mock 与真实 RESTful API 快速切换。
- **后端架构**：
  - 基于 Python 3.12+、FastAPI 与 SQLAlchemy 异步 ORM。
  - 内置基于 Argon2-cffi 的高强度密码哈希与逐接口 RBAC 鉴权机制。
  - 支持登录失败限流防御与审计日志追踪。
  - 集成 Alembic 实现规范的数据库版本迁移与 Schema 隔离集成测试。
- **部署与容器化**：
  - 提供生产级 `compose.yaml` 配置，支持单机 Docker 一键完成 PostgreSQL、数据迁移、初始化及 API/Web 服务拉起。
