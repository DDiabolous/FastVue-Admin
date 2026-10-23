# 二次开发指南

## 更换品牌与模块

复制 `frontend/.env.example` 为 `.env.local`，修改 `VITE_APP_TITLE`。侧边栏、登录页和页面标题使用同一品牌配置。Logo 图形目前位于登录页和侧边栏，可替换相应图标。

`VITE_STORAGE_PREFIX` 用于隔离默认系统演示数据、Token 和主题。旧的 `iot_*`、`ent_*`、`hub_*` 数据不会自动迁入新的系统模块。

`VITE_APP_PRESET=full` 启用旧行业示例，`VITE_ENABLE_ORGANIZATION=true` 单独启用组织示例。默认均关闭；关闭的模块不注册路由，直接访问会进入 404。旧行业页面仍是独立本地 Mock 示例，存储键及数据结构未迁移，不受新存储前缀隔离。若不需要，可以删除对应配置和页面目录。

完整演示入口为 `npm run dev:full`。如 `.env.local` 显式设置了模式或模块开关，会优先使用 `.env.local`。

## 新增一个页面

1. 在 `src/views/` 创建业务目录。
2. 在 `src/config/modules.js` 的 `modules` 中添加定义，例如：

```js
{
  path: '/articles',
  name: 'Articles',
  title: '文章管理',
  group: '内容管理',
  icon: 'Document',
  permission: 'content:article:read',
  component: () => import('@/views/articles/index.vue'),
}
```

侧边栏和路由自动使用该定义，首页的最近访问也会记录该页面。只读菜单配置页展示当前启用的定义。

3. 在权限选项配置与真实后端中增加对应权限码。若继续使用前端 Mock，需要扩展 Mock 的权限选项和接口实现。
4. 在页面使用 `PageContainer` 包裹内容，通过 `actions` 插槽添加页面操作。参考 `views/examples/List.vue`。

## 复用列表与表单

- `PageContainer`：标题、说明、页面操作插槽。
- `TableToolbar`：主要操作、选中数量、列设置与表格密度；刷新统一使用顶栏入口。
- `StatusTag`：启用、停用状态展示。
- `v-auth="'system:users:create'"`：控制按钮可见性；数组表示任一权限满足即可。

批量按钮放在表格上方的唯一工具栏中。没有选中项时禁用，选中后显示数量，不另加重复操作栏。

当前系统用户、角色和字典共享 `ResourcePage.vue`，字段位于 `config/resources.js`。字段差异较小的资源可复用此页；复杂业务优先使用插槽及独立页面，避免把所有交互塞进配置。

## 接入后端

先按 [后端说明](../backend/README.md) 启动 PostgreSQL、执行迁移并初始化管理员。设置 `VITE_USE_MOCK=false` 和 `VITE_API_BASE_URL=/api/v1`，重启开发服务。Vite 已配置 `/api` 转发到 `http://127.0.0.1:8001`。默认 API 使用原生 fetch；接口方法位于 `src/api/admin.js`，请求处理位于 `src/api/adminRequest.js`。

真实请求按 `{ code: 200, message, data }` 解包。HTTP 或业务 401 会清理会话并返回登录；403 保留登录并展示操作错误。受保护路由初始化会通过 `/admin/me` 获取资料和权限。网络失败保留登录状态，显示错误，用户可重试。

实际部署时配置同源 `/api` 代理，或由后端允许所需的跨域来源。环境变量是公开的构建参数，不得填入服务端密钥。Web History 模式需要让前端路由回退到 `index.html`，并将 `/api` 单独转发到服务端。

权限码必须与后端一致。前端隐藏按钮和拦截路由只负责交互，后端仍须验证认证、功能权限和数据访问范围。

菜单目前由代码配置；若后续加入服务端菜单，只允许将返回的组件标识映射到预先注册的组件，不能执行服务端返回的代码。

## 演示数据和权限

默认演示数据库保存在 IndexedDB 的 `${VITE_STORAGE_PREFIX}:demo-v2` 中，旧版 localStorage 数据会自动迁移。需要重置演示数据时，可在浏览器开发者工具中删除该 IndexedDB 数据库，并清除 localStorage 的 `${VITE_STORAGE_PREFIX}:token` 后刷新。

内置 admin 用户与角色受保护，个人资料和密码在个人中心修改。编辑用户可维护用户和字典，不能分配超出自身权限的角色。只读用户无法新增、编辑和删除。权限与角色状态修改后会影响 Mock API 的后续请求；核心后端在每次请求执行对应校验，使用数据库会话与服务端审计。

旧页面 `views/admin-accounts/index.vue`、`roles/index.vue`、`dictionary/index.vue`、`settings/index.vue`、`profile/index.vue` 已由 `views/system/` 替代且未注册路由，仅保留原始实现供迁移参考。新增功能应放在新目录，不再扩展旧页面。

## 验证

```bash
cd frontend
npm test
npm run build
npm run build:full
```

人工检查管理员与只读账号的菜单差异、刷新恢复会话、CRUD、修改密码及关闭模块后的 404。文件示例演示选择、裁剪、本地图片预览及模拟上传进度，真实上传需新增接口、授权、大小限制及服务端类型校验。

## 界面偏好与高频操作

顶部搜索支持 `⌘ K` / `Ctrl K`，可以按名称、分组和路径搜索，并通过上下方向键、Enter 打开页面；结果遵循当前账号权限。

点击页面标题旁的星标可收藏到工作台。收藏由当前浏览器保存，工作台只展示当前启用且有权访问的页面。项目介绍移入工作台的“项目帮助”，日常首页优先呈现收藏、功能导航及最近访问。

“界面设置”抽屉提供五种主题色、浅色/深色/跟随系统、舒适/紧凑表格密度。设置即时生效并保存在 `${VITE_STORAGE_PREFIX}:appearance`。系统配色发生变化时，跟随系统模式会同步更新。

用户、角色、字典、日志及基础列表示例使用 `useTablePreferences`，保存列显隐、拖动后的列宽、已提交筛选词与分页；按账号 ID 和页面隔离。至少保留一个数据列，“列设置 → 重置”可以恢复列布局。刷新按钮会重新获取数据并保留筛选；“重置”清除筛选。全局表格密度同时适用于默认页面与 full 模式的业务列表。

`useUnsavedChanges` 为系统编辑弹窗、系统配置和个人资料提供离开确认及浏览器关闭提示。新增表单页面可复用该组合函数；保存成功后更新初始快照。浏览器关闭提示的实际显示由浏览器策略决定。

新增视觉变量和响应式规则位于 `src/styles/admin.css`，外观参数集中在 `utils/preferences.js` 与 `stores/app.js`。`TableEmpty` 统一处理加载中、空数据、筛选无结果及失败重试状态；`TableToolbar` 提供列设置与密度入口。

默认主题色为蓝色（`#2563eb`），已保存的自定义颜色继续保留；可在界面设置中“恢复默认外观”。顶部主题按钮使用圆形视图过渡：暗色从按钮中心展开，亮色通过暗色快照向按钮中心收起。浏览器不支持 View Transitions 或用户启用减少动态效果时，直接完成主题切换。


## Full 模式的业务页面

会员、设备、资产、组织和监控页面共用 `PageContainer`，由主内容区承担纵向滚动，不再使用独立的固定高度页面。列表横向滚动和终端日志内部滚动仍保留。

- `FilterPanel` 提供统一的筛选布局；高级筛选仍由页面插槽控制。
- `StatisticCard` 统一会员与设备页的统计卡片，支持图标、单位、说明和语义色。
- `TableToolbar` 的 `tools` 插槽承载列表/卡片视图切换，批量操作和选中数量只展示一次。
- `useBusinessTable` 在保留业务单元格插槽的前提下，复用列显隐、列宽、筛选、分页和视图偏好。偏好按账号与页面保存；组织的树形名称列固定显示。切换筛选、分页或视图时清空旧选择，避免对不可见记录执行批量操作。
- `useBusinessDraft` 为主要新增/编辑弹窗提供未保存提示，与默认页面行为一致。

业务页面公共样式放在 `src/styles/business.css`，品牌色使用外观变量，在线、预警、离线等状态保留语义色；终端区域保留适合日志阅读的深色背景。弹窗和抽屉宽度适应小屏幕，表单字段在手机上切换为单列。

full 业务示例继续使用原有浏览器 Mock 数据，未接入核心后端。统计卡片中的演示指标不代表真实业务监控。


## 后端模块与接口版本

核心后端按 `api → services → repositories → models` 分工，配置、异常、安全与启动检查在 `core/`，连接池与 ORM 基类在 `db/`。新增业务时分别添加模型、Schema、Repository、Service、v1 路由及迁移，按接口调用方在 `app/api/v1/admin/router.py` 或 `app/api/v1/user/router.py` 注册新路由。已有核心 CRUD 可参考用户或字典模块。

Service 负责业务校验与事务提交，Repository 负责查询及持久化，不在 HTTP 路由中写 SQL。业务错误使用 `AppError`，成功写操作与审计日志在同一事务中提交。新增 API 版本时在 `app/api/router.py` 并行挂载版本路由，保留已发布版本的输入输出契约；API 版本与数据库迁移版本独立管理。

当前业务 Base URL 为 `/api/v1`，健康检查仍为 `/api/health`。已有 `.env.local` 若覆盖为 `/api`，需要同步修改并重启 Vite。Mock 调用继续使用 `/admin/auth/login` 等相对资源路径，其行为不受 HTTP 版本前缀影响。

## 开发示例复用

开发示例使用“项目管理”串联页面，可在默认模式与 full 模式下使用。页面右上角的“页面用法”提供适用范围、源码位置和复用内容；隐藏页面大标题后，该入口仍然保留。

| 页面 | 复用内容 |
| --- | --- |
| 基础列表 `/examples/list` | 多条件查询、排序、分页、多选删除、列设置、状态预览；页内切换列表与卡片，共享筛选、字段显隐、数据及详情抽屉 |
| 表单与详情 `/examples/form` | 分步填写、分类与负责人联动、唯一编号校验、计划周期、未保存提醒 |
| 复杂详情 `/examples/details` | 描述列表、项目进度、交付阶段、时间线和编辑入口 |
| 树形列表 `/examples/tree` | 目录过滤、表格定位、父级调整、拖拽排序、增删改 |
| 文件上传 `/examples/upload` | 图片裁剪、附件校验、本地模拟上传、取消、失败重试 |
| 导入导出 `/examples/import-export` | CSV 校验、异常行导出、重复邮箱跳过或更新、按筛选或选中项导出 |
| 交互反馈 `/examples/feedback` | 删除确认、空状态、错误重试、权限反馈和成功结果 |

项目示例由 `src/stores/exampleProjects.js` 共享内存数据，刷新后恢复初始项目；目录和人员导入数据仅保留在当前页面。所有示例都不写入真实业务后端。上传进度和失败是可主动触发的本地演示，生产环境需要替换为真实上传请求及取消机制。详情中的交付阶段根据项目进度推导，用于演示关联表格。

列表与卡片已合并为“基础列表”一个菜单，页内切换视图保留筛选条件；旧地址 `/examples/cards` 自动跳转到 `/examples/list`。开发示例和可选模块、业务示例共用 `business-page`、`business-data-card`、`business-overlay` 样式，通用实体卡片复用 `entity-card-grid` 与 `entity-card`，示例专属细节集中在 `styles/examples.css`。

复用时保留 `PageContainer`、`FilterPanel`、`TableToolbar`、`TableEmpty`、`useTablePreferences`、`useUnsavedChanges` 等组件和交互，将示例 Store 替换为业务接口，并对编号唯一性、授权和文件类型等规则增加服务端验证。
