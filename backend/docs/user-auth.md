# 用户注册与认证接口

注册用户使用 PostgreSQL `users` 表和独立 Redis 命名空间，与后台管理员 `admin_accounts`、后台会话完全分开。
不使用 Cookie，不修改 Web 页面。生产环境通过 HTTPS 提供服务。

## 部署与配置

在 backend 目录执行：

```bash
uv sync
uv run alembic upgrade head
```

在 `backend/.env` 配置：

```dotenv
# 独立的随机签名密钥，至少 32 字节；禁止复用默认 SECRET_KEY。
USER_JWT_SECRET=<独立随机密钥>
USER_JWT_ISSUER=ws-fastvue-user
USER_REFRESH_TOKEN_DAYS=7
USER_AUTH_REDIS_PREFIX=fastvue:user:auth
REDIS_URL=redis://localhost:6379/0
# 生产环境必须关闭模拟模式，并配置真实网关。
USER_SMS_MOCK_ENABLED=false
SMS_GATEWAY_URL=https://your-sms-gateway.example/send
SMS_GATEWAY_TOKEN=<网关鉴权令牌>
ENVIRONMENT=production
```

可用 `uv run python -c 'import secrets; print(secrets.token_urlsafe(48))'` 生成签名密钥，并妥善保存。
`USER_REFRESH_TOKEN_DAYS` 允许 7–30 天；访问令牌固定 15 分钟。配置修改后重启服务。
当前实现使用 Redis 单实例或主从实例；Lua 原子操作负责核销验证码、计数及轮换。
Redis 需要按持久化及高可用要求部署；缓存不可用时认证返回 503，不降级放行。
签名密钥缺失时返回 503。短信模拟模式默认关闭；生产环境显式开启会导致配置校验失败并拒绝启动。
本地联调可使用 `ENVIRONMENT=development` 和 `USER_SMS_MOCK_ENABLED=true`，此时不需要短信网关，不会发送真实短信。
任意六位 ASCII 数字均通过核验（例如 `123456`、`000000`），无需先调用 send-code；不核验过期、核销或场景对应关系。
关闭模拟模式后才启用下文的真实验证码安全规则；网关未配置时返回 503。
密码登录、JWT 校验、设备会话和权限隔离在模拟模式下仍正常执行。

### 通用 HTTP 短信网关约定

后端向 `SMS_GATEWAY_URL` 发送 POST：

```http
Authorization: Bearer <SMS_GATEWAY_TOKEN>
Content-Type: application/json
```

```json
{
  "phone": "+8613900000000",
  "scene": "register",
  "code": "123456",
  "ttl_seconds": 300
}
```

网关接受发送任务后应返回 2xx 和 JSON `{"success":true}`；可附带 `request_id`。
非 2xx、`success` 不为 true、网络错误或超时均作为发送失败，接口返回 503。
生产环境要求网关 HTTPS 且配置鉴权令牌，不跟随重定向，超时 5 秒，不自动重试，避免重复付费。
网关需将该约定映射到实际短信服务商的签名、模板和发送 API。
测试通过依赖注入短信发送器和 MockTransport 验证，不发送真实短信。

## 通用约定

- 用户接口前缀：`/api/v1/user`；沿用目标仓库后台路径 `/api/v1/admin/auth/*`、`/api/v1/admin/accounts`。两套账号及令牌互不通用。
- 请求/响应为 JSON；成功结构：`{"code":200,"message":"success","data":...}`。
- HTTP 错误状态为 400 / 401 / 403 / 409 / 422 / 429 / 503，同时返回同名 `code`、`message` 和 `data:null`。
- 401 表示访问或刷新凭证无效；429 携带 `Retry-After` 秒数，客户端应停止重试并等待。
- 手机号支持中国大陆 11 位号码或 E.164 格式，统一存储为 E.164（大陆号码补 `+86`）。
- 验证码必须是 6 位 ASCII 数字字符串，密码长度为 8–128 字符，保留空格、不做 trim。
- `device_id` 是客户端稳定生成的非空设备标识，最长 128 字符，无空白；它不是鉴权凭证。
- 接口禁止额外请求字段；日期为 ISO 8601 带时区字符串。用户 ID 为 32 位字符串。
- 令牌及用户信息响应使用 `Cache-Control: no-store`，服务端不记录验证码或原始令牌。

## 1. 发送验证码

`POST /auth/send-code`

```json
{"phone":"13900000000","scene":"register"}
```

`scene`：`register` / `login` / `reset_pwd` / `delete_account`。
注销场景为独立扩展，需携带本人访问令牌且手机号必须匹配；其余三个场景无需登录。
成功返回：

```json
{"code":200,"message":"验证码已发送","data":{"expires_in":300,"retry_after":60}}
```

同一手机号跨场景、跨号码写法共享 60 秒冷却（模拟发送接口也保留限流）。以下验证码核销规则仅在关闭模拟模式后生效：验证码按场景隔离，有效 5 分钟，Redis 只存 HMAC 摘要，成功验证立即删除。
连续 5 次错误校验会销毁该验证码。另有每手机号滚动 24 小时 10 次、每来源 IP 每小时 30 次发送上限。
来源 IP 使用 ASGI 的客户端地址，不直接信任任意 `X-Forwarded-For`；反向代理部署需显式配置 uvicorn 可信代理范围。

## 2. 用户注册（注册即登录）

`POST /auth/register`

```json
{"phone":"13900000000","code":"123456","password":"YourPassword123!","device_id":"android-device-A"}
```

使用 `register` 验证码；重复手机号返回 409。
密码使用 Argon2id，独立随机盐，64 MiB / 3 轮 / 4 路并行，仅保存哈希。
成功返回与登录相同的双令牌和用户信息。

## 3. 用户登录

`POST /auth/login`

密码登录：

```json
{"phone":"13900000000","login_type":"password","credential":"YourPassword123!","device_id":"android-device-A"}
```

短信登录：

```json
{"phone":"13900000000","login_type":"sms","credential":"123456","device_id":"android-device-A"}
```

短信方式在模拟模式下接受任意六位数字，真实模式使用 `login` 场景验证码。密码或凭证错误统一返回 401。
5 分钟窗口内第 6 次失败起锁定该手机号 15 分钟（符合“失败超 5 次”），锁定期间正确密码也无法登录。
每来源 IP 另限 5 分钟内 60 次登录尝试；成功登录清空该号码失败计数。
同一设备重新登录会使此前该设备的会话失效；不同设备可分别登录，最多保留 10 个设备会话，超出时淘汰最早到期的会话。

成功数据示例：

```json
{
  "code":200,
  "message":"success",
  "data":{
    "access_token":"<JWT>",
    "refresh_token":"<opaque-refresh-token>",
    "token_type":"bearer",
    "expires_in":900,
    "refresh_expires_in":604800,
    "user":{
      "id":"<32-character-id>",
      "phone":"+8613900000000",
      "nickname":"用户0000",
      "avatar_url":"",
      "membership":{"level":"free","is_active":false,"expires_at":null}
    }
  }
}
```

## 4. 无感刷新

`POST /auth/refresh`

```json
{"refresh_token":"<refresh-token>"}
```

无需访问令牌，成功 `data` 返回全新的 `access_token`、`refresh_token`、`token_type`、`expires_in`、`refresh_expires_in`。
刷新令牌为高熵不透明随机凭证，Redis 只保存 HMAC 摘要；不会作为 JWT 解码。
轮换后旧刷新令牌和旧访问令牌立即失效；并发使用同一刷新令牌只允许一个请求成功，其余返回 401。
刷新令牌有效期从成功轮换时重新计算为配置的 7–30 天。

Android 底层拦截器应对刷新实行 single-flight：多个 401 共用一次刷新结果，原请求最多重试一次，
刷新失败后清除本地登录态。所有 token 均从 JSON 收发，客户端不需要 Cookie。

## 5. 重置密码

`POST /auth/reset-password`

```json
{"phone":"13900000000","code":"123456","new_password":"NewPassword123!"}
```

使用 `reset_pwd` 场景验证码。更新 Argon2id 哈希及账号认证版本，并删除该用户所有 Redis 会话。
全部设备的访问、刷新令牌立即失效，需重新登录；验证码不能重复使用。
成功 `data:null`。

## 6. 退出当前设备

`POST /auth/logout`

```http
Authorization: Bearer <access_token>
```

```json
{"refresh_token":"<refresh-token>"}
```

访问令牌与刷新令牌必须属于同一个用户、同一个设备会话。仅撤销当前设备，其他设备不受影响。
撤销后该设备的访问和刷新令牌均失效。重复使用已失效凭证返回 401。成功 `data:null`。

## 7. 获取当前用户

`GET /me`

```http
Authorization: Bearer <access_token>
```

返回与登录 `user` 相同的资料结构，包括昵称、头像、手机号和会员状态。过期会员按免费状态返回。
此接口校验 JWT 签名、固定 HS256 算法、issuer、audience、scope、令牌类型、有效期、必要 claims，
并检查数据库账号状态/认证版本与 Redis 当前设备会话。App 令牌无法调用管理接口，后台令牌也无法用于 App。

## 8. 注销账号

`POST /auth/delete-account`

```http
Authorization: Bearer <access_token>
```

密码二次验证：

```json
{"password":"YourPassword123!"}
```

或提供验证码（模拟模式任意六位数字；真实模式需本人已登录状态下申请的 `delete_account` 验证码）：

```json
{"code":"123456"}
```

两个字段必须且只能提供一个。验证失败会计入该手机号的登录失败锁定计数。
确认后账号标记为 `deleted`、记录 `deleted_at`，移除手机号、昵称、头像及密码哈希，清除会员状态和全部 Redis 会话。
本次实现立即注销，不设置冷静期；保留用户 ID 与注销时间以供关联记录审计。
手机号释放后可重新注册，生成新用户 ID；历史令牌不能访问新账号。
成功 `data:{"status":"deleted"}`。

## 测试

```bash
# PostgreSQL 必须显式设置 TEST_DATABASE_URL，Redis 默认使用本机 15 号测试库，PostgreSQL 每次使用随机独立 schema。
# 可通过 USER_AUTH_TEST_REDIS_URL 修改 Redis 测试连接。
TEST_DATABASE_URL='<专用 PostgreSQL 测试连接>' uv run --locked pytest tests/test_user_auth.py tests/test_sms_gateway.py -q
```

真实验证码测试会显式关闭模拟模式，模拟模式另有独立测试。测试 Redis 采用随机命名空间，不执行 FLUSHDB；数据库只清理测试中生成的账号。
OpenAPI 契约在 `/openapi.json`，交互文档在 `/docs`。

## 实现参考

JWT 的固定算法、issuer/audience 和必要 claims 验证参考 [PyJWT 官方 API](https://pyjwt.readthedocs.io/en/stable/api.html)。
验证码与令牌轮换的多步原子操作参考 [Redis Lua 官方说明](https://redis.io/docs/latest/develop/programmability/functions-intro/)。

## 迁移说明与统一命名

产品用户使用独立的 `users` 表，不赋予后台角色；后台账号存储于 `admin_accounts`。
接口、模型、Schema 和服务按 `admin/`、`user/` 业务域分目录；Python 字段及函数使用 snake_case、类型使用 PascalCase。

| 用途 | 当前文件 / 类型 |
| --- | --- |
| 产品认证接口 | `api/v1/user/auth.py` |
| 产品资料接口 | `api/v1/user/profile.py` |
| 产品令牌校验 | `core/user_security.py` |
| 产品认证请求与响应 | `schemas/user/auth.py` |
| 产品账号资料 | `schemas/user/accounts.py` |
| 产品认证业务与会话 | `services/user/auth.py`、`services/user/auth_store.py` |
| 产品账号 | `models/user/accounts.py` / `UserAccount` |
| 后台账号 | `models/admin/accounts.py` / `AdminAccount` |
| 后台角色 | `models/admin/roles.py` / `AdminRole` |
| 测试 | `tests/test_user_auth.py` |

配置项 `USER_JWT_*`、`USER_AUTH_REDIS_PREFIX` 保留原名及默认值，以兼容现有部署和会话。`USER_SMS_MOCK_ENABLED` 默认关闭，生产环境禁止开启；本地联调需显式开启。
历史迁移不改写；`0006` 重命名后台账号与角色表，`0007` 重命名产品账号、后台会话和登录限流表；`0008` 将产品账号表从 `app_accounts` 重命名为 `users`。升级前停止后端，执行 `uv run --locked alembic upgrade head`，再启动新版。

响应字段沿用本仓库 `message`（原中台为 `msg`），客户端据此调整。JWT 内部 scope/audience 仍为 `app`，仅表示终端用户认证域；签名密钥、issuer、Redis 前缀均独立配置。
历史 Alembic 迁移保持不变；`0005` 引入产品账号表，后续版本执行表重命名。

### 首次部署

复制 `.env.example` 为 `.env`，配置实际 `DATABASE_URL`、`REDIS_URL` 和独立的 `USER_JWT_SECRET` 后运行：

```bash
uv sync --locked
uv run --locked alembic upgrade head
# 目标后台尚未初始化时执行，交互输入管理员密码：
uv run --locked python -m app.cli init
```

不要把源中台的 `backend_accounts` 或管理员会话复制到本仓库。Docker Compose 使用独立 Redis 服务，签名密钥从根目录 `.env` 的 `USER_JWT_SECRET` 注入。

### 迁移现有注册用户数据

暂停旧用户接口写入后，在本仓库 backend 目录执行：

```bash
# 先检查源数据；不连接目标数据库、不写入任何数据。
uv run --locked python -m app.migrate_user_accounts --source-env /path/to/source/backend/.env --dry-run
# .env 中 DATABASE_URL 指向目标数据库；完成迁移建表后导入。
uv run --locked python -m app.migrate_user_accounts --source-env /path/to/source/backend/.env
```

保留用户 ID、Argon2id 哈希、手机号、会员资料、状态和时间。完整事务导入，完全一致的记录跳过，冲突拒绝并回滚，不覆盖目标数据。
源数据库只读，导入后保留源记录，确认切换前不删表。Redis 会话和验证码不迁移，用户需重新登录。

### 独立 HTML 联调工具

保留 `tools/user-auth-tester.html` 用于注册、登录、验证码、刷新、退出及注销接口联调。
后端地址默认 `http://localhost:8001`，工具自动附加 `/api/v1/user`。
在 backend 目录运行 `python3 -m http.server 5173 --directory tools`，打开 `http://localhost:5173/user-auth-tester.html`；也可通过 IDE 的 63342 端口预览。
默认 CORS 允许 `localhost`、`127.0.0.1` 的 5173 和 63342 端口。显式设置 `CORS_ORIGINS` 时需包含实际页面来源（协议、主机及端口，不含路径），修改后重启后端。
短信模拟模式默认关闭；如需本地模拟，应显式设置 `USER_SMS_MOCK_ENABLED=true`，生产环境禁止开启。
工具将测试凭证保存在浏览器 localStorage，可点击“清空本地凭证”清理；请使用测试账号。

产品接口现使用 `/api/v1/user/*`，原 `/api/v1/app/*` 返回 404；升级需执行迁移至 `0008`，不会重建或清空账号。JWT 内部 claims、签名密钥及 Redis 命名空间保持兼容，以保留现有会话。
