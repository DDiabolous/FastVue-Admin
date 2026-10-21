# 前端 API 契约

当前无后端实现。以下约定由默认前端 API 层和 Mock 行为共同定义，作为后续后端的接入基准。

## 通用约定

Base URL 默认 `/api`；除登录外使用 `Authorization: Bearer <token>`。请求体为 JSON，所有响应采用：

```json
{ "code": 200, "message": "操作成功", "data": {} }
```

列表：`data = { "list": [], "total": 0 }`。分页参数 `page` 从 1 开始，`pageSize` 默认 10，最大 200；`keyword` 为关键词。HTTP 401/403/404/405/422/500 应与语义一致，错误响应同样包含 `code` 和 `message`。

## 认证与个人资料

| 方法 | 路径 | 请求或响应 data |
| --- | --- | --- |
| POST | `/auth/login` | 请求 `{username,password}`；返回 `{token,user}` |
| GET | `/auth/me` | 返回用户资料与权限 |
| GET | `/auth/roles` | 返回当前操作者可分配的启用角色 `[{roleKey,roleName}]`，不暴露角色管理接口 |
| POST | `/auth/logout` | 注销当前会话 |
| PATCH | `/auth/profile` | 请求 `{realName,email}`；返回更新后的用户资料 |
| POST | `/auth/password` | 请求 `{oldPassword,newPassword}`；更新后撤销该用户全部会话，客户端重新登录 |

用户资料至少包含 `id, username, realName, role, roleName, email, status, permissions`，不得返回密码或密码哈希。`permissions` 是权限码数组；`*` 表示全部权限。

## 系统资源

`users`、`roles`、`dictionary` 三种资源使用统一 URL：

| 方法 | 路径 | 行为 |
| --- | --- | --- |
| GET | `/<resource>?page=1&pageSize=10&keyword=` | 查询分页 |
| POST | `/<resource>` | 新增 |
| PATCH | `/<resource>/:id` | 部分更新 |
| DELETE | `/<resource>/:id` | 删除 |

权限按 `system:<resource>:read/create/update/delete` 验证。

| 资源 | 写入字段 |
| --- | --- |
| users | `username, realName, email, role, status`，新增需要 `password`，编辑时密码留空不更新 |
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
