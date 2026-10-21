# FastVue-Admin 前端

通用后台开发底座，默认启用系统基础功能与开发示例。详细说明见 [项目 README](../README.md)。

```bash
npm ci
npm run dev          # 精简启动
npm run dev:full     # 含行业和组织示例
npm test
npm run build
npm run build:full   # 构建完整演示
npm run preview     # 预览最近一次构建
```

建议使用 Node.js 22.12+。配置参考 [.env.example](.env.example)，构建产物位于 `dist/`。`.env.local` 的显式配置会覆盖模式文件，切换 full 模式时请注意模块开关。

默认使用浏览器 Mock，真实后端尚未实现。接入后端时配置 `VITE_USE_MOCK=false` 和 `VITE_API_BASE_URL`，并遵循接口约定。

- [二次开发指南](../docs/development.md)
- [API 约定](../docs/api.md)
- [MIT 开源许可](../LICENSE)
