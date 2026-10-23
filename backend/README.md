# FastVue-Admin 后端

FastAPI + SQLAlchemy 2 异步 ORM + PostgreSQL 的通用后台核心，产品用户认证使用 Redis 管理验证码与设备会话。业务接口挂载在 `/api/v1`，与现有系统页面使用同一契约。Python 3.12+，默认并仅验证 PostgreSQL（本地验证版本 17）。

## 常用命令

先准备 PostgreSQL 并配置 `backend/.env`，以下命令在 `backend/` 执行：

`DATABASE_URL` 为必填配置，不提供默认连接。可通过 `backend/.env` 或进程环境变量设置；缺失、空值或不支持的连接格式会阻止启动。配置有效后，启动过程还会检查数据库连接、迁移版本及初始化状态。

| 场景 | 命令 |
| --- | --- |
| 首次准备 / 更新数据库 | `uv run --locked manage.py setup` |
| 本地开发 | `uv run --locked manage.py dev` |
| 生产准备 / 升级 | `uv run --locked --no-dev manage.py setup` |
| 生产启动 | `uv run --locked --no-dev manage.py serve` |
| 查看命令帮助 | `uv run --locked manage.py --help` |

`setup` 合并迁移与按需初始化，重复执行不会重置账号。`dev` 默认开启重载，`serve` 默认关闭重载，二者默认监听 `127.0.0.1:8001` 并关闭代理头信任。

后台账号存储在 `admin_accounts`，后台角色存储在 `admin_roles`；产品用户存储在 `users`。
迁移 `0006` 将原 `users`、`roles` 表直接重命名，保留账号、角色和会话外键关系。
升级已有环境时先停止后端服务，执行 `uv run --locked alembic upgrade head`，再启动新版后端。
后台接口统一为 `/api/v1/admin/*`，产品接口统一为 `/api/v1/user/*`；保留 `system:users:*`、`system:roles:*` 权限键。迁移 `0007` 将后台会话与限流表重命名为 `admin_sessions`、`admin_login_buckets`；`0008` 将产品用户表由 `app_accounts` 重命名为 `users`，保留原有数据。

## Python 环境与依赖

默认使用 [uv](https://docs.astral.sh/uv/) 管理 Python 和项目依赖，版本要求为 0.12.18+。`pyproject.toml` 声明依赖，`uv.lock` 锁定解析结果，`.python-version` 指定 Python 3.12；这些文件均应提交到 Git。

`uv sync --locked` 自动创建或同步 `backend/.venv` 并安装开发依赖，不需要手动激活环境；本机缺少匹配解释器时，uv 会自动下载。后续命令统一通过 `uv run --locked` 执行，锁文件与配置不一致时会报错，避免启动时隐式更新依赖。

添加运行依赖使用 `uv add 包名`，开发工具使用 `uv add --dev 包名`；更新依赖后提交 `pyproject.toml` 和 `uv.lock`，并重新测试。升级已有依赖使用 `uv lock --upgrade-package 包名`，再执行 `uv sync --locked`。不再单独维护 requirements 文件。

## 本地启动

先准备 PostgreSQL 数据库和独立用户；产品用户认证还需可用的 Redis。可使用本机 PostgreSQL，在 `psql` 中创建：

```sql
CREATE ROLE fastvue LOGIN;
\password fastvue
CREATE DATABASE fastvue OWNER fastvue;
```

也可在项目根目录复制 `.env.example` 为 `.env`，设置随机 `POSTGRES_PASSWORD` 后运行 `docker compose up -d db`。Compose 密码建议仅使用字母、数字、`-`、`_`，以便直接组成连接 URL；如自行配置含特殊字符的密码，需在连接 URL 中编码。

```bash
cd backend
cp .env.example .env
# 编辑 .env 中的 DATABASE_URL，填入实际数据库账号与密码
# 产品认证同时配置 REDIS_URL、USER_JWT_SECRET；短信模拟默认关闭
uv run --locked manage.py setup
uv run --locked manage.py dev
```

`setup` 自动执行 Alembic 迁移，首次运行时初始化管理员；再次运行只应用待执行迁移，保留现有数据和密码，不再询问密码。uv 会自动准备依赖和虚拟环境，不必另行执行同步命令。

以后启动只需在 `backend/` 运行 `uv run --locked manage.py dev`，可用 `--port 8001` 修改端口。启动仍会检查数据库，不会自动迁移或重置账号。

`setup` 和独立的 `init` 命令会交互读取首次管理员密码（8–128 位），账号为 `admin`；也可从进程环境变量 `ADMIN_PASSWORD` 读取，便于自动化部署。密码不写入命令参数、响应或审计日志。初始化必须显式执行，启动服务不会创建固定密码账号。重复初始化不覆盖数据和密码。

初始化默认创建 admin/editor/viewer 三个角色，仅创建管理员账号。开发环境需要演示用户时，可以在**首次初始化**使用 `uv run --locked manage.py setup --demo`，额外创建 `editor/editor123`、`viewer/viewer123`；正式环境请省略 `--demo`。已有数据库不会因重复加 `--demo` 自动补种。

前端在 `frontend/.env.local` 设置：

```dotenv
VITE_USE_MOCK=false
VITE_API_BASE_URL=/api/v1
```

然后在 `frontend/` 执行 `npm ci && npm run dev`。Vite 默认将 `/api` 代理到 `http://127.0.0.1:8001`，如需其他地址，在启动 Vite 前设置 `API_PROXY_TARGET`。切换真实 API 与 Mock 时请退出旧会话，二者使用不同的身份与数据。

- API 文档：[打开接口文档](http://127.0.0.1:8001/docs)
- 就绪检查：[检查服务状态](http://127.0.0.1:8001/api/health)。数据库连接、迁移与管理员初始化正常才返回 200。
- 接口契约：[docs/api.md](../docs/api.md)

## 服务器部署（uv）

在服务器安装 uv 并准备 PostgreSQL，配置 `backend/.env` 后，在 `backend/` 目录执行：

```bash
uv run --locked --no-dev manage.py setup
uv run --locked --no-dev manage.py serve
```

生产命令使用 `--no-dev`，不安装测试与格式化工具；不启用自动重载。由 systemd 等进程管理器托管时，将工作目录设置为服务器上的 `backend/`，启动命令使用 uv 的实际绝对路径，运行账号应能读取项目配置并维护其 `.venv`。环境变量由进程管理器或后端 `.env` 提供，前端通过反向代理访问 API。

后续更新代码时，先备份数据库，再执行 `uv run --locked --no-dev manage.py setup`，最后重启 API 服务。普通重启只需 `uv run --locked --no-dev manage.py serve`。`setup` 是显式准备/升级命令，`dev` 和 `serve` 都只启动并检查服务。

## Docker Compose

项目根目录提供 PostgreSQL、Redis、一次性迁移、初始化、API 和 Nginx 前端服务。后端镜像内使用固定版本 uv 和 `uv sync --locked --no-dev` 创建运行环境，再通过 `.venv/bin` 中的命令启动；无需在宿主机额外安装 Python：

```bash
cp .env.example .env
# 编辑 .env，替换 POSTGRES_PASSWORD 并设置独立的 USER_JWT_SECRET
docker compose --profile tools run --build --rm init
docker compose up --build -d web
```

`init` 在迁移完成后读取管理员密码。非交互环境可通过根目录 `.env` 设置 `ADMIN_PASSWORD`，初始化后删除该配置。前端默认发布到 [本机 8080 端口](http://localhost:8080)，构建时关闭 Mock。数据库数据保存在 `postgres_data` 卷中；正常升级不要删除此卷。

升级代码后重新构建镜像，先运行 `docker compose run --rm migrate`，再重建 `api` 和 `web`。迁移需先备份数据库；破坏性降级仅供开发验证。

API 不发布宿主机端口，只有 Compose 内部网络可访问。Nginx 是唯一 HTTP 入口并覆盖 `X-Forwarded-For`；Compose 中 API 因此信任内部代理头。本地命令关闭代理头信任。自行部署反向代理时，应显式设置 Uvicorn 的 `--forwarded-allow-ips` 为可信代理 IP 或网段，禁止将信任所有代理的 API 端口公开。正式对外服务需由入口代理提供 HTTPS。

本地 PostgreSQL 路径已执行迁移、测试和前端联调；Compose 文件与 Dockerfile 已做静态检查，仍需在具备 Docker 的环境中验证容器启动。

## 启动与运行检查

API 每次启动都会在接收请求前检查 PostgreSQL 连接、Alembic 迁移版本、系统配置及启用的内置管理员和角色。检查限制为 10 秒，连接失败、超时或状态不完整会输出不含连接凭据的错误并退出；不会自动迁移或植入管理员。按错误提示修复连接，或先执行迁移和初始化后再启动。

运行期间 `/api/health` 继续执行相同检查，数据库不可用时返回 503。连接池在取连接时也会检测连接存活；数据库恢复后可重新建立连接。

## 模块与安全行为

- 后台认证：Argon2id 密码哈希；高熵随机 Bearer Token；数据库只保存 Token 的 SHA-256 摘要，默认 8 小时过期。
- 会话撤销：退出注销当前会话；修改/重置密码、禁用账号、切换角色撤销该用户全部会话；禁用角色撤销绑定用户会话。重新启用不会恢复旧 Token。
- 权限：每次请求读取当前账号及角色，逐接口校验；角色权限修改在下一请求生效。前端已缓存的菜单权限在重新获取 `/admin/me` 后更新。
- 授权范围：角色授权不得超过操作者已有权限，禁止维护权限更高的角色或用户，不能通过创建用户或角色获得 `*`。
- 管理员保护：内置管理员账号与角色不可经通用 CRUD 修改或删除；个人资料和密码通过本人接口维护。
- 数据完整性：账号、角色标识、字典类型与值的唯一性受数据库约束；被引用角色不可删除或改标识。
- 登录限流：基于数据库、按真实来源 IP 计数，默认每 900 秒最多 10 次登录尝试，多个进程共享；达到限制返回 429 和 `Retry-After`。成功尝试也计入窗口。
- 审计：服务端记录登录成功、失败、限流、退出及系统写操作。写操作与成功审计同事务提交；不保存密码、请求体或 Token，不提供清空日志接口。
- 配置：`/api/v1/admin/settings/public` 仅公开应用名称与介绍，其余配置由后台权限控制。`registration` 表示备案信息，不是开放注册开关；后台账号不开放自助注册，产品用户通过 `/api/v1/user/auth/register` 注册。
- 事务：使用 PostgreSQL 事务级 advisory lock 协调授权读取和写操作，避免权限校验与修改之间的竞态。当前核心写请求串行，适合管理后台；扩展高吞吐业务时应拆分锁范围并补充并发测试。

时间统一以 UTC ISO 8601 输出，列表按创建时间倒序及 ID 稳定排序；字典优先按 `sort` 升序。分页参数非法返回 422，唯一约束或引用冲突返回 409。数据库异常回滚，对外不暴露 SQL 或连接信息。

## 配置

后端 `.env` 固定从 `backend/` 读取，不依赖启动目录；进程环境变量优先。示例见 [.env.example](.env.example)。

| 变量 | 默认值 | 含义 |
| --- | --- | --- |
| `DATABASE_URL` | 无，必填 | 显式配置 `postgresql+asyncpg://` 连接，缺失或无效时阻止启动 |
| `CORS_ORIGINS` | localhost / 127.0.0.1 的 5173、63342 来源 | JSON 数组，只允许显式来源；同源部署可设 `[]` |
| `SESSION_HOURS` | `8` | 会话有效小时数 |
| `LOGIN_LIMIT` | `10` | 每来源 IP 窗口内登录尝试上限 |
| `LOGIN_WINDOW_SECONDS` | `900` | 登录限流窗口秒数 |
| `ENVIRONMENT` | `development` | 生产部署设为 `production` |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | 产品认证的验证码、限流和设备会话存储 |
| `USER_JWT_SECRET` | 无 | 产品认证独立随机签名密钥，至少 32 字节 |
| `USER_JWT_ISSUER` | `ws-fastvue-user` | 产品访问令牌 issuer |
| `USER_REFRESH_TOKEN_DAYS` | `7` | 刷新令牌有效天数，允许 7–30 天 |
| `USER_AUTH_REDIS_PREFIX` | `fastvue:user:auth` | 产品认证 Redis 命名空间 |
| `USER_SMS_MOCK_ENABLED` | `false` | 仅本地联调可开启；生产环境开启会拒绝启动 |
| `SMS_GATEWAY_URL` / `SMS_GATEWAY_TOKEN` | 无 | 真实短信网关地址和鉴权令牌 |

生产环境可定期执行 `uv run --locked --no-dev python -m app.cli cleanup` 清理过期会话和限流记录；不会删除审计日志。新增模型后使用 `uv run --locked alembic revision --autogenerate -m "..."` 生成迁移，人工复核后执行 `uv run --locked alembic upgrade head`。

## 测试

```bash
uv sync --locked
# 使用专用测试数据库，不要填写生产数据库
export TEST_DATABASE_URL='postgresql+asyncpg://fastvue:your-password@127.0.0.1:5432/fastvue_test'
uv run --locked pytest
uv run --locked ruff check app tests alembic
uv run --locked alembic check
```

测试在指定数据库中创建随机 schema，执行真实 Alembic 迁移和初始化，结束后删除测试 schema，不清空 public 数据。测试账号需有该数据库的 CREATE 权限；未配置 `TEST_DATABASE_URL` 时数据库测试跳过。`uv run --locked alembic check` 使用正常 `DATABASE_URL` 检查模型与已迁移数据库是否一致。

## 目录与扩展

```text
manage.py                     简化启动、初始化与升级入口
app/
  main.py                     应用组装、生命周期和健康检查
  core/                       配置、安全、业务异常、响应及启动检查
  db/                         ORM 基类、连接池和请求会话管理
  api/
    router.py                 /api 下的版本路由汇总
    v1/
      router.py               /v1 下的 admin/user 路由汇总
      admin/
        router.py             /api/v1/admin
        dependencies.py       后台认证、权限及审计上下文
        auth.py               /auth/*
        accounts.py           /accounts/*
        roles.py              /roles/*
        profile.py            /me
        dictionary.py         /dictionary/*
        settings.py           /settings/*
        logs.py               /logs
      user/
        router.py             /api/v1/user
        dependencies.py       产品账号数据库会话
        auth.py               /auth/*
        profile.py            /me
  models/admin/               后台账号、角色、会话及系统资源模型
  models/user/                 产品账号模型
  schemas/admin/              后台请求与响应契约
  schemas/user/                产品认证及账号契约
  schemas/common.py           共享输入类型及分页契约
  services/admin/             后台业务、权限及审计
  services/user/               产品认证及 Redis 会话
  services/sms.py             短信网关适配
  repositories/admin/         后台数据查询与持久化
  repositories/base.py        通用 Repository 基类
  cli.py                      初始化和过期数据清理命令
alembic/                      数据库版本迁移
tools/user-auth-tester.html    产品认证 HTML 联调测试台
docs/user-auth.md              产品认证部署与接口契约
tests/                        PostgreSQL 与 API 契约测试
pyproject.toml                项目依赖与开发依赖组
uv.lock                       uv 依赖锁文件
.python-version               默认 Python 版本
```

目录按账号域划分：例如 `/api/v1/admin/accounts` 对应 `api/v1/admin/accounts.py`，业务服务为 `services/admin/accounts.py`，模型为 `models/admin/accounts.py`。目录已表达业务域，文件名不重复添加 `admin_`、`user_`；类型仍使用 `AdminAccount`、`UserAccount`，避免跨域导入混淆。仅接口层保留版本目录，服务与模型可供后续 API 版本复用。

API 路由仅处理参数、依赖和响应，具体业务由对应 Service 执行；Service 通过 Repository 访问数据库，并统一提交写操作及其审计日志。请求会话管理器负责异常回滚与释放连接，不再在路由和依赖中重复提交事务。业务错误通过 `core/errors.py` 的 `AppError` 表达，由 HTTP 层统一映射，Service 不依赖 FastAPI 的 Request 或 HTTPException。

用户、角色、字典各有独立 Service 和 Repository，通用分页及 CRUD 流程可以复用基类；新增资源无需修改按资源名称分支的中心函数。用户列表批量查询角色，避免逐行查询。

业务版本挂载在 `api/router.py`，当前为 `/api/v1`。将来新增 v2 时并行挂载新路由，按需增加新的请求/响应 Schema 或适配逻辑，复用业务服务和模型；`/api/health` 不随业务版本变化。Swagger 文档根据实际路由生成。升级需执行 Alembic 迁移至 `0009`，保留原有数据和会话；旧业务 URL 返回 404。

新增权限时同步修改 `app/core/admin_permissions.py` 与前端 `config/permissions.js`，为新模块增加模型、Schema、Service、路由、迁移及越权测试。菜单继续由前端代码声明，未提供动态菜单 CRUD。

组织、设备、资产、会员和监控仍为 full 模式本地示例；多租户、数据范围权限、上传存储、工作流、支付、邮件与真实设备通信不在本版范围。

采用 [MIT License](../LICENSE)。

## 注册用户认证

产品用户使用 `/api/v1/user/auth/*` 注册、登录、刷新、重置密码和注销，通过 `GET /api/v1/user/me` 查询基础资料。账号存储于 `users`，与后台账号、角色和令牌独立；后台账号没有自助注册接口。

产品端访问令牌固定 15 分钟，刷新令牌轮换，Redis 不可用时返回 503；配置签名密钥后才可使用产品认证。生成密钥：

```bash
uv run --locked python -c "import secrets; print(secrets.token_urlsafe(32))"
```

将输出填入 `backend/.env` 的 `USER_JWT_SECRET`，配置 Redis 和真实短信网关后重启后端。本地需要短信模拟时，显式设置 `USER_SMS_MOCK_ENABLED=true`；生产环境禁止开启。完整契约见 [产品用户认证文档](docs/user-auth.md)。

### HTML 联调测试台

保留 [tools/user-auth-tester.html](tools/user-auth-tester.html)。在后端已启动的情况下，另开终端，在 `backend/` 目录运行：

```bash
python3 -m http.server 5173 --directory tools
```

打开 [联调测试台](http://localhost:5173/user-auth-tester.html)，后端地址填写 `http://localhost:8001`，工具自动附加 `/api/v1/user`。也可使用 IDE 63342 端口预览，默认 CORS 已放行 `localhost`、`127.0.0.1` 的 5173 和 63342 来源。

若 5173 已由前端占用，可改用其他端口，并将实际来源添加到 `CORS_ORIGINS` 后重启后端；例如 5174 对应 `http://localhost:5174`。不要通过 `file://` 打开。显式设置的 CORS 列表会覆盖默认值，必须包含页面实际使用的协议、主机和端口。Compose 使用同源代理，默认 `CORS_ORIGINS=[]`，API 8001 端口不向宿主机发布。

测试台将凭证保存于浏览器 localStorage，请使用测试账号，结束后点击“清空本地凭证”。

产品资料新增 `gender`、`birthday`、`city`、`email`、`bio`，通过 `PATCH /api/v1/user/me` 修改；邮箱仅作联系资料，不用于登录。迁移 `0009` 新增资料字段并删除两个会员字段及其数据，接口不再返回会员信息。详见 [产品认证文档](docs/user-auth.md)。
