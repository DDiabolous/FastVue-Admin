# FastVue-Admin

基于 Vue 3、Element Plus、Pinia 和 Vite 的通用后台开发底座。默认界面不绑定设备、资产或企业组织，适合在此基础上开发内容、运营、电商、内部工具等后台。

提供精简模板与完整业务演示两种模式，便于从基础管理功能开始，按需扩展业务模块。提供 Vue 前端、浏览器 Mock 和基于 FastAPI + PostgreSQL 的核心后端，可按需选择纯前端演示或全栈运行。

## 功能特性

- **基础管理**：用户、角色、数据字典、系统设置、日志和个人中心。
- **模块配置**：菜单、路由与访问权限共用模块声明，支持按模式启用功能。
- **开发示例**：列表、表单详情、树形列表和本地文件选择。
- **界面定制**：默认蓝色主题，支持切换主题色、亮暗模式和表格密度；主题按钮提供圆形展开与收起动画。
- **操作效率**：`⌘/Ctrl + K` 搜索页面，收藏与最近访问，表格列显隐、列宽及查询偏好持久化。
- **统一布局**：复用页面容器、筛选面板、统计卡片与表格工具栏，适配移动端。
- **数据接入**：统一请求层支持 Mock 与真实 HTTP 切换，提供接口约定文档。

## 快速启动

建议使用 Node.js 22.12+ 和 npm。在仓库根目录执行：

```bash
cd frontend
npm ci
npm run dev
```

默认地址为 [本机 5173 端口](http://localhost:5173)；端口占用时，以终端输出为准。

初始演示账号：

| 账号 | 密码 | 权限 |
| --- | --- | --- |
| admin | admin123 | 全部系统功能 |
| editor | editor123 | 用户和字典的查看、维护 |
| viewer | viewer123 | 用户和字典只读 |

Mock 数据保存在当前浏览器中，修改后会持久保存，密码修改后使用新密码登录。Mock 认证和本地权限仅用于演示，不能作为生产环境的安全边界。

## 启动真实后端

后端使用 uv 管理 Python 环境与依赖，采用 Python 3.12+、FastAPI、SQLAlchemy 异步 ORM 和 PostgreSQL。完整步骤见 [后端启动与部署](backend/README.md)。准备数据库并配置 `backend/.env` 后：

```bash
cd backend
uv run --locked manage.py setup
uv run --locked manage.py dev
```

`setup` 合并数据库迁移和按需初始化，后续启动只需运行 `uv run --locked manage.py dev`。初始化时设置管理员密码，账号为 `admin`，默认不会创建固定密码演示用户。前端在 `frontend/.env.local` 设置 `VITE_USE_MOCK=false`、`VITE_API_BASE_URL=/api/v1`，重启 Vite 即可；开发代理默认转发到本机 8000 端口。

也可使用根目录的 Docker Compose 配置完成数据库迁移、初始化和部署。后端具备服务端会话撤销、逐接口权限、登录限流和审计日志；API 文档位于 `http://127.0.0.1:8000/docs`。

## 两种启动模式

- `npm run dev`：精简启动，包含工作台、系统管理、日志、个人中心和开发示例。
- `npm run dev:full`：完整演示，额外启用设备、资产、会员、服务监控及组织示例。
- `npm run build` / `npm run build:full`：构建对应版本。
- `npm run preview`：本地预览最近一次构建的产物。
- `npm test`：验证演示认证、授权、持久化、审计及主题切换逻辑。

以上命令均在 `frontend/` 目录执行。构建产物位于 `frontend/dist/`，可部署到静态站点服务；部署时需为前端路由配置回退到 `index.html`。

## 配置与二次开发

可参考 [frontend/.env.example](frontend/.env.example) 创建 `frontend/.env.local`，只填写需要覆盖的配置：

| 配置项 | 用途 | 默认值 |
| --- | --- | --- |
| `VITE_APP_TITLE` | 应用名称 | `FastVue-Admin` |
| `VITE_STORAGE_PREFIX` | 浏览器存储前缀 | `fastvue` |
| `VITE_USE_MOCK` | 是否使用浏览器 Mock | `true` |
| `VITE_API_BASE_URL` | 后端接口地址 | `/api/v1` |
| `VITE_APP_PRESET` | 模块预设 | `starter` |
| `VITE_ENABLE_ORGANIZATION` | 是否启用组织示例 | `false` |

环境变量修改后需重启开发服务。`.env.local` 中显式配置的值会覆盖模式文件；若需要通过 `dev:full` 切换完整演示，请勿在 `.env.local` 固定精简模式的模块开关。

新增页面时，在 `src/config/modules.js` 注册模块，并按需扩展页面、API 与权限配置。详细步骤见 [二次开发指南](docs/development.md)，后端对接见 [接口约定](docs/api.md)。

## 已实现与接入边界

默认系统页面通过 `src/api/` 访问数据，支持 Mock 与真实 HTTP 两种实现。核心后端已实现认证、用户、角色、字典、配置及审计；设置 `VITE_USE_MOCK=false` 后可连接 PostgreSQL 后端。

- 菜单、路由和访问权限统一由 `src/config/modules.js` 声明。
- 用户、角色、数据字典支持基础增删改查，用户创建需设置至少 8 位密码。
- 菜单配置页为只读预览，修改代码配置后生效，不提供运行时菜单管理。
- Mock 模式日志记录浏览器演示事件；真实 API 模式由服务端记录登录与关键写操作审计。
- 列表、树形列表、表单详情、文件选择示例不依赖具体业务；上传示例不发送文件。
- 可选组织与行业示例仍使用原有 `mockData.js`，仅供界面参考，不属于真实 API 接入范围；仅管理员可访问。
- 多租户、数据范围授权、真实监控、文件存储、邮件通知尚未实现。

## 目录

```text
frontend/src/
  api/                 统一请求与接口方法
  config/              应用、模块、权限和资源字段配置
  mock/                默认系统模块的浏览器演示适配器
  components/admin/    页面容器、筛选面板、统计卡片、表格工具栏
  composables/         表格偏好、业务列表和表单草稿等复用逻辑
  directives/          v-auth 权限指令
  views/system/        默认系统页面
  views/examples/      行业无关的开发示例
  views/equipment/     可选业务示例，复用模板 UI（其余同类目录见文档）
backend/               FastAPI 核心后端、PostgreSQL 迁移与集成测试
compose.yaml           数据库、迁移、API 与前端容器配置
docs/                  二次开发与接口约定
LICENSE                MIT 开源许可
```

## 参与贡献

欢迎通过 Issue 报告问题或提出建议，也欢迎提交 Pull Request。提交前请在 `frontend/` 目录运行 `npm test`、`npm run build` 和 `npm run build:full`；涉及界面的调整请附上对应模式和截图。后端改动需运行 PostgreSQL 集成测试及迁移检查，方法见后端 README。

## 开源许可

本项目采用 [MIT License](LICENSE)，版权归属为 `Copyright (c) 2026 DDiabolous`。第三方依赖及素材遵循各自的许可声明。
