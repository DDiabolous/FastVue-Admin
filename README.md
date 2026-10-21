# FastVue-Admin

基于 Vue 3、Element Plus、Pinia 和 Vite 的通用后台开发底座。默认界面不绑定设备、资产或企业组织，适合在此基础上开发内容、运营、电商、内部工具等后台。

## 启动

```bash
cd frontend
npm ci
npm run dev
```

默认地址为 http://localhost:5173。构建环境需使用满足当前 Vite 版本要求的 Node.js（建议 Node 22.12+）。

初始演示账号：

| 账号 | 密码 | 权限 |
| --- | --- | --- |
| admin | admin123 | 全部系统功能 |
| editor | editor123 | 用户和字典的查看、维护 |
| viewer | viewer123 | 用户和字典只读 |

Mock 数据保存在当前浏览器中，修改后会持久保存，密码修改后使用新密码登录。Mock 认证和本地权限仅用于演示，不能作为生产环境的安全边界。

## 两种启动模式

- `npm run dev`：精简启动，包含工作台、系统管理、日志、个人中心和开发示例。
- `npm run dev:full`：完整演示，额外启用设备、资产、会员、服务监控及组织示例。
- `npm run build` / `npm run build:full`：构建对应版本。
- `npm test`：验证演示认证、授权、持久化及审计逻辑。

可复制 `frontend/.env.example` 为 `frontend/.env.local`，修改品牌、存储前缀、API 地址和模块开关。环境变量修改后需重启开发服务；`.env.local` 中显式配置的值会覆盖模式文件。

## 已实现与接入边界

默认系统页面通过 `src/api/` 访问数据，支持 Mock 与真实 HTTP 两种实现。真实后端尚未实现；`VITE_USE_MOCK=false` 后需要接入符合接口约定的服务。

- 菜单、路由和访问权限统一由 `src/config/modules.js` 声明。
- 用户、角色、数据字典支持基础增删改查，用户创建需设置至少 8 位密码。
- 菜单配置页为只读预览，修改代码配置后生效，不提供运行时菜单管理。
- 登录和操作日志记录当前浏览器内的演示事件，不代表真实服务端审计。
- 列表、树形列表、表单详情、文件选择示例不依赖具体业务；上传示例不发送文件。
- 可选组织与行业示例仍使用原有 `mockData.js`，仅供界面参考，不属于真实 API 接入范围；仅管理员可访问。
- 多租户、数据范围授权、真实监控、文件存储、邮件通知尚未实现。

## 目录

```text
frontend/src/
  api/                 统一请求与接口方法
  config/              应用、模块、权限和资源字段配置
  mock/                默认系统模块的浏览器演示适配器
  components/admin/    页面容器、表格工具栏、状态标签
  directives/          v-auth 权限指令
  views/system/        默认系统页面
  views/examples/      行业无关的开发示例
  views/equipment/     可选的旧业务示例（其余同类目录见文档）
docs/                  二次开发与接口约定
backend/PROMPT.MD      未来后端实现提示词；当前不含后端代码
```

开发者指南见 [docs/development.md](docs/development.md)，接口契约见 [docs/api.md](docs/api.md)。

本轮未替项目选择开源许可证；正式发布前请维护者补充 LICENSE 并确认现有素材及依赖的许可要求。
