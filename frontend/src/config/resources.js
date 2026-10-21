export const resources = {
  users: {
    title: '用户管理',
    description: '维护后台登录账号及其角色。业务会员和客户数据由独立模块管理。',
    columns: [
      { prop: 'username', label: '账号' },
      { prop: 'realName', label: '姓名' },
      { prop: 'roleName', label: '角色' },
      { prop: 'email', label: '邮箱' },
    ],
    fields: [
      { prop: 'username', label: '账号', required: true },
      { prop: 'realName', label: '姓名', required: true },
      { prop: 'email', label: '邮箱', type: 'email' },
      { prop: 'role', label: '角色', type: 'role', required: true },
      { prop: 'password', label: '密码', type: 'password' },
    ],
    defaults: { username: '', realName: '', email: '', role: 'viewer', password: '', status: 1 },
  },
  roles: {
    title: '角色管理',
    description: '通过权限码统一控制菜单访问和页面操作。数据范围授权由接入的后端扩展。',
    columns: [
      { prop: 'roleName', label: '角色名称' },
      { prop: 'roleKey', label: '角色标识' },
      { prop: 'description', label: '说明' },
    ],
    fields: [
      { prop: 'roleName', label: '角色名称', required: true },
      { prop: 'roleKey', label: '角色标识', required: true },
      { prop: 'description', label: '说明', type: 'textarea' },
      { prop: 'permissions', label: '功能权限', type: 'permissions' },
    ],
    defaults: { roleName: '', roleKey: '', description: '', permissions: [], status: 1 },
  },
  dictionary: {
    title: '数据字典',
    description: '维护状态、分类等可复用选项。同一字典类型下的字典值应当唯一。',
    columns: [
      { prop: 'type', label: '字典类型' },
      { prop: 'label', label: '显示名称' },
      { prop: 'value', label: '字典值' },
      { prop: 'sort', label: '排序' },
    ],
    fields: [
      { prop: 'type', label: '字典类型', required: true },
      { prop: 'label', label: '显示名称', required: true },
      { prop: 'value', label: '字典值', required: true },
      { prop: 'sort', label: '排序', type: 'number' },
    ],
    defaults: { type: '', label: '', value: '', sort: 0, status: 1 },
  },
}
