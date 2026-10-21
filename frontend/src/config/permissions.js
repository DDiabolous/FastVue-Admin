export const permissionGroups = [
  { label: '用户管理', key: 'users', actions: ['read', 'create', 'update', 'delete'] },
  { label: '角色管理', key: 'roles', actions: ['read', 'create', 'update', 'delete'] },
  { label: '数据字典', key: 'dictionary', actions: ['read', 'create', 'update', 'delete'] },
  { label: '系统配置', key: 'settings', actions: ['read', 'update'] },
  { label: '日志管理', key: 'logs', actions: ['read'] },
  { label: '菜单配置', key: 'menus', actions: ['read'] },
]
export const permissionOptions = permissionGroups.flatMap((group) =>
  group.actions.map((action) => ({
    value: `system:${group.key}:${action}`,
    label: `${group.label} · ${{ read: '查看', create: '新增', update: '编辑', delete: '删除' }[action]}`,
  })),
)
export const hasPermission = (permissions, required) =>
  !required ||
  permissions.includes('*') ||
  (Array.isArray(required)
    ? required.some((key) => permissions.includes(key))
    : permissions.includes(required))
