# 核心 API 契约

核心后端位于 `backend/`，使用 FastAPI 和 PostgreSQL，实现以下接口；浏览器 Mock 保留相同前端调用结构。启动及认证策略见 [后端说明](../backend/README.md)。

## 通用约定

业务接口 Base URL 为 `/api/v1`；除登录、公开配置与健康检查外使用 `Authorization: Bearer <token>`。请求体为 JSON，所有响应采用：

```json
{ "code": 200, "message": "操作成功", "data": {} }
```

列表：`data = { "list": [], "total": 0 }`。分页参数 `page` 从 1 开始，`pageSize` 默认 10，最大 200；`keyword` 为关键词。HTTP 400/401/403/404/405/409/422/429/500/503 应与语义一致，错误响应同样包含 `code` 和 `message`。

## 认证与个人资料

| 方法 | 路径 | 请求或响应 data |
| --- | --- | --- |
| POST | `/admin/auth/login` | 请求 `{username,password}`；返回 `{token,user}` |
| GET | `/admin/me` | 返回用户资料与权限 |
| GET | `/admin/auth/roles` | 返回当前操作者可分配的启用角色 `[{roleKey,roleName}]`，不暴露角色管理接口 |
| POST | `/admin/auth/logout` | 注销当前会话 |
| PATCH | `/admin/me` | 请求 `{realName,email}`；返回更新后的用户资料 |
| POST | `/admin/auth/password` | 请求 `{oldPassword,newPassword}`；更新后撤销该用户全部会话，客户端重新登录 |

用户资料至少包含 `id, username, realName, role, roleName, email, status, permissions`，不得返回密码或密码哈希。`permissions` 是权限码数组；`*` 表示全部权限。

## 系统资源

`accounts`、`roles`、`dictionary` 三种后台资源使用统一 URL：

| 方法 | 路径 | 行为 |
| --- | --- | --- |
| GET | `/admin/<resource>?page=1&pageSize=10&keyword=` | 查询分页 |
| POST | `/admin/<resource>` | 新增 |
| PATCH | `/admin/<resource>/:id` | 部分更新 |
| DELETE | `/admin/<resource>/:id` | 删除 |

权限按 `system:<resource>:read/create/update/delete` 验证，其中 `accounts` 资源沿用 `system:users:*` 权限键。

| 资源 | 写入字段 |
| --- | --- |
| accounts | `username, realName, email, role, status`，新增需要 `password`，编辑时密码留空不更新 |
| roles | `roleKey, roleName, description, permissions[], status` |
| dictionary | `type, label, value, sort, status` |

每条记录有 `id` 和 `createdAt`。用户列表额外包含 `roleName`；密码不在列表中返回。`status` 为 1（启用）或 0（停用）。`username` 和 `roleKey` 唯一；字典的 `(type,value)` 唯一。字典类型通过 `type` 字符串分组，此版本不提供独立字典类型实体。

内置管理员与管理员角色不得通过资源接口修改或删除。已绑定用户的角色不能删除或修改标识。不得删除当前用户，也不得维护超出操作者可管理范围的用户。可分配角色的权限不能超出操作者自身权限；具体授权策略应在服务端实现。

## 系统配置与日志

- `GET /settings`：`system:settings:read`。
- `PATCH /settings`：`system:settings:update`，字段 `{siteName,description,contactEmail,registration}`。
- `GET /logs?category=login|operation&page=1&pageSize=10&keyword=`：`system:logs:read`，返回分页数据，字段 `id,time,operator,action,target,category,status,ip`。日志只读。

应用品牌由构建配置决定；`settings.siteName` 是保存在服务端的应用资料。此版本不自动将其应用到导航品牌，避免依赖配置读取权限。

## 当前不属于接口契约的功能

菜单页面是代码配置预览，未请求 `/menus`；对应访问权限为 `system:menus:read`。开发示例中的列表、表单和文件选择在内存中运行。可选组织、会员、设备、资产和监控页面使用旧本地演示数据，尚未接入此 API 层。


## 后端运行约定

- `GET /api/health`：无需认证，数据库连接、迁移及管理员初始化正常返回 200，否则返回 503；数据库类型为 PostgreSQL。
- `GET /api/v1/admin/settings/public`：无需认证，只返回 `{siteName,description}`，不公开联系邮箱及其余管理配置。
- 时间为 UTC ISO 8601。列表按创建时间倒序与 ID 稳定排序；字典优先按 `sort` 升序。
- 非法分页、未知写入字段、无效权限码及参数校验失败返回 422；标识重复和数据库引用冲突返回 409。
- 用户名、角色标识为 1–64 位字母、数字、下划线、点或短横线。密码长度为 8–128 位；编辑用户时密码为空或省略保持不变。
- 仅 `*` 表示全部权限，不支持其他权限通配表达式。角色授权不能超过操作者已有权限，也不能维护权限更高的用户或角色。
- 默认会话有效期为 8 小时，服务端保存随机 Token 的 SHA-256 摘要。退出撤销当前会话；密码修改/重置、账号停用或角色切换撤销用户全部会话；角色停用撤销绑定用户的会话。权限变更在后续请求立即生效。
- 登录限流默认每来源 IP 在 900 秒内允许 10 次尝试（含成功），超限返回 429 和 `Retry-After`。可信代理设置及可配置参数见后端 README。
- 成功写操作与审计日志同事务提交；日志不记录密码、Token 或请求体。

开发示例和 full 业务页仍使用本地数据。Mock 的演示账号与真实数据库相互独立；API 模式使用初始化时设置的管理员密码。


## API 版本策略

业务接口按 URL 版本组织，当前仅实现 `/api/v1`；表格中的资源路径相对于该 Base URL。基础设施接口 `/api/health` 保持独立，不加业务版本号。`/docs` 和 `/openapi.json` 展示实际注册的版本路由及输入、输出 Schema。

旧的 `/api/auth/*`、`/api/users` 等未版本化业务地址已移除，访问返回 404。现有接入方需将 Base URL 从 `/api` 改为 `/api/v1`；请求响应字段及权限码保持一致；后台账号、角色和产品账号分别存储于 `admin_accounts`、`admin_roles`、`app_accounts`，升级需执行迁移。反向代理仍转发整个 `/api/` 前缀，不要剥离 `/v1`。

兼容性新增字段与修复继续留在 v1。不兼容的参数、响应或行为变化应新增 `app/api/v2/` 并在 `app/api/router.py` 挂载；按需要定义新的 Schema 和适配逻辑，保持 v1 契约及测试。Service、Repository 和数据库模型按业务复用，无需为 API 版本复制整套数据表。当前不提供 v2 接口。


## 产品用户账号

产品用户使用 `/api/v1/app/auth/*` 注册、登录、刷新和退出，`GET /api/v1/app/me` 获取当前账号。
其 JWT 与后台会话令牌互不通用，后台账号没有产品端自助注册入口。完整契约见 [产品认证文档](../backend/docs/app-auth.md)。

数据库表为 `admin_accounts`、`admin_roles`、`app_accounts`；后台会话及登录限流表为 `admin_sessions`、`admin_login_buckets`。
升级前停止后端，在 `backend` 执行 `uv run --locked alembic upgrade head`，再部署新版后端及前端。
原 `/api/v1/auth/*`、`/api/v1/users`、`/api/v1/user/*` 不再提供。前端登录态存储键改为 `admin_token`，升级后需重新登录。
