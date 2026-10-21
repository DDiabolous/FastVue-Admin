// Universal Mock Data and LocalStorage persistence for Universal Admin & Operations Platform
// Suitable for any Web Admin / SaaS / Enterprise / Operations / Hardware Management system

// 1. Initial Department & Team Hierarchy (Universal Enterprise & Cloud SaaS Structure)
const INITIAL_DEPARTMENTS = [
  {
    id: 100,
    deptName: '云枢数字科技集团总部',
    deptCode: 'CORP_HQ',
    leader: '张志远',
    phone: '13800100000',
    email: 'corp@cloudhub-admin.com',
    status: 1,
    orderNum: 1,
    createTime: '2024-01-01 09:00:00',
    children: [
      {
        id: 101,
        deptName: '技术研发与数字化中心',
        deptCode: 'TECH_CENTER',
        leader: '李晓峰',
        phone: '13800100001',
        email: 'tech@cloudhub-admin.com',
        status: 1,
        orderNum: 1,
        createTime: '2024-01-15 10:00:00',
        children: [
          {
            id: 102,
            deptName: '前端架构与应用研发组',
            deptCode: 'TECH_FE',
            leader: '周子文',
            phone: '13800100002',
            email: 'fe@cloudhub-admin.com',
            status: 1,
            orderNum: 1,
            createTime: '2024-02-01 09:30:00'
          },
          {
            id: 103,
            deptName: '后端微服务与云原生组',
            deptCode: 'TECH_BE',
            leader: '陈思宇',
            phone: '13800100003',
            email: 'be@cloudhub-admin.com',
            status: 1,
            orderNum: 2,
            createTime: '2024-02-01 09:30:00'
          },
          {
            id: 104,
            deptName: '数据智能与算法工程组',
            deptCode: 'TECH_AI',
            leader: '王明翰',
            phone: '13800100004',
            email: 'ai@cloudhub-admin.com',
            status: 1,
            orderNum: 3,
            createTime: '2024-03-01 14:00:00'
          }
        ]
      },
      {
        id: 105,
        deptName: '产品设计与用户体验中心',
        deptCode: 'PROD_DESIGN',
        leader: '张雅婷',
        phone: '13912345678',
        email: 'product@cloudhub-admin.com',
        status: 1,
        orderNum: 2,
        createTime: '2024-02-10 11:00:00',
        children: [
          {
            id: 106,
            deptName: '用户体验与交互设计组',
            deptCode: 'PROD_UX',
            leader: '刘启明',
            phone: '13912345679',
            email: 'ux@cloudhub-admin.com',
            status: 1,
            orderNum: 1,
            createTime: '2024-03-10 10:00:00'
          },
          {
            id: 107,
            deptName: '商业化产品规划与增长组',
            deptCode: 'PROD_BIZ',
            leader: '赵雷',
            phone: '13912345680',
            email: 'growth@cloudhub-admin.com',
            status: 1,
            orderNum: 2,
            createTime: '2024-03-15 15:30:00'
          }
        ]
      },
      {
        id: 108,
        deptName: '基础设施与网络工程部',
        deptCode: 'INFRA_ENG',
        leader: '孙德胜',
        phone: '13700100005',
        email: 'infra@cloudhub-admin.com',
        status: 1,
        orderNum: 3,
        createTime: '2024-02-15 09:00:00',
        children: [
          {
            id: 109,
            deptName: '分布式云网关与系统组',
            deptCode: 'INFRA_CLOUD',
            leader: '魏建国',
            phone: '13700100006',
            email: 'cloud@cloudhub-admin.com',
            status: 1,
            orderNum: 1,
            createTime: '2024-03-20 10:00:00'
          },
          {
            id: 110,
            deptName: '智能终端与硬件接入组',
            deptCode: 'INFRA_DEVICES',
            leader: '韩梅梅',
            phone: '13700100007',
            email: 'terminals@cloudhub-admin.com',
            status: 1,
            orderNum: 2,
            createTime: '2024-03-25 11:00:00'
          }
        ]
      },
      {
        id: 111,
        deptName: '运营管理与客户成功中心',
        deptCode: 'BIZ_OPERATIONS',
        leader: '林宛如',
        phone: '13611112222',
        email: 'ops@cloudhub-admin.com',
        status: 1,
        orderNum: 4,
        createTime: '2024-01-20 10:00:00'
      },
      {
        id: 112,
        deptName: '财务管理与法务审计部',
        deptCode: 'FINANCE_AUDIT',
        leader: '王丽华',
        phone: '13633334444',
        email: 'audit@cloudhub-admin.com',
        status: 1,
        orderNum: 5,
        createTime: '2024-01-25 10:00:00'
      }
    ]
  }
]

// 2. Initial Roles (Universal RBAC Role Matrix)
const INITIAL_ROLES = [
  {
    id: 1,
    roleKey: 'super_admin',
    roleName: '超级系统管理员',
    description: '系统最高全局管理权限，拥有全部组织、用户、资产、字典与系统配置权限',
    dataScope: 'ALL',
    status: 1,
    orderNum: 1,
    createTime: '2024-01-01 09:00:00',
    permissionKeys: ['dashboard', 'users', 'users:add', 'users:edit', 'users:delete', 'departments', 'roles', 'devices', 'devices:add', 'devices:edit', 'devices:cmd', 'dictionary', 'monitor', 'settings', 'profile']
  },
  {
    id: 2,
    roleKey: 'operation_manager',
    roleName: '业务与运营总监',
    description: '负责平台业务运营、资产终端监控调度、服务健康大屏及日常业务运维',
    dataScope: 'DEPT_AND_CHILD',
    status: 1,
    orderNum: 2,
    createTime: '2024-01-10 10:00:00',
    permissionKeys: ['dashboard', 'users', 'departments', 'devices', 'devices:add', 'devices:edit', 'devices:cmd', 'monitor', 'profile']
  },
  {
    id: 3,
    roleKey: 'tech_developer',
    roleName: '技术开发主管',
    description: '负责系统服务对接、数据字典配置、系统API调试、微服务监控与参数设置',
    dataScope: 'DEPT_ONLY',
    status: 1,
    orderNum: 3,
    createTime: '2024-02-01 11:30:00',
    permissionKeys: ['dashboard', 'devices', 'dictionary', 'monitor', 'settings', 'profile']
  },
  {
    id: 4,
    roleKey: 'compliance_auditor',
    roleName: '安全合规审计员',
    description: '只读审查全系统操作日志、访问轨迹及安全登录策略，保障平台合规运行',
    dataScope: 'ALL',
    status: 1,
    orderNum: 4,
    createTime: '2024-03-01 14:00:00',
    permissionKeys: ['dashboard', 'users', 'settings', 'profile']
  },
  {
    id: 5,
    roleKey: 'guest_user',
    roleName: '访客与只读员工',
    description: '受限访客角色，仅具备概览看板与个人基本信息查看权限',
    dataScope: 'SELF',
    status: 1,
    orderNum: 5,
    createTime: '2024-04-01 09:00:00',
    permissionKeys: ['dashboard', 'profile']
  }
]

// 3. Initial Users (Universal Admin User Pool)
const INITIAL_USERS = [
  {
    id: 'USR-1001',
    username: 'admin',
    realName: '系统总管理员',
    role: 'super_admin',
    roleName: '超级系统管理员',
    phone: '13800138000',
    email: 'admin@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    department: '技术研发与数字化中心',
    deptId: 101,
    jobTitle: '平台总架构师',
    bio: '致力于构建高性能、高可用且通用的现代化数字管理系统架构。',
    gender: '男',
    securityScore: 90,
    enable2FA: false,
    lastLoginTime: '2026-10-20 15:30:10',
    lastLoginIp: '192.168.1.108',
    createdAt: '2024-01-10 09:00:00'
  },
  {
    id: 'USR-1002',
    username: 'operator',
    realName: '张建国',
    role: 'operation_manager',
    roleName: '业务与运营总监',
    phone: '13912345678',
    email: 'operator@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    department: '运营管理与客户成功中心',
    deptId: 111,
    jobTitle: '运营业务负责人',
    bio: '专注平台全链路业务流程梳理与精细化运营指标优化。',
    gender: '男',
    securityScore: 85,
    enable2FA: false,
    lastLoginTime: '2026-10-20 14:15:22',
    lastLoginIp: '192.168.2.45',
    createdAt: '2024-03-15 14:30:00'
  },
  {
    id: 'USR-1003',
    username: 'developer',
    realName: '周子文',
    role: 'tech_developer',
    roleName: '技术开发主管',
    phone: '13788889999',
    email: 'dev@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
    department: '前端架构与应用研发组',
    deptId: 102,
    jobTitle: '高级研发工程师',
    bio: '追求极致交互体验与干净模块化代码工程。',
    gender: '男',
    securityScore: 88,
    enable2FA: true,
    lastLoginTime: '2026-10-20 13:45:10',
    lastLoginIp: '192.168.1.142',
    createdAt: '2024-06-20 10:15:00'
  },
  {
    id: 'USR-1004',
    username: 'auditor',
    realName: '王丽华',
    role: 'compliance_auditor',
    roleName: '安全合规审计员',
    phone: '13611112222',
    email: 'auditor@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/2/3a/057d60ff3123896541f4864c3c399png.png',
    department: '财务管理与法务审计部',
    deptId: 112,
    jobTitle: '合规风控审计专员',
    bio: '坚守合规底线，确保平台全流程安全与数据隐私可靠。',
    gender: '女',
    securityScore: 95,
    enable2FA: true,
    lastLoginTime: '2026-10-18 16:02:18',
    lastLoginIp: '192.168.1.5',
    createdAt: '2024-08-01 11:00:00'
  },
  {
    id: 'USR-1005',
    username: 'guest',
    realName: '陈访客',
    role: 'guest_user',
    roleName: '访客与只读员工',
    phone: '13566667777',
    email: 'guest@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg',
    department: '产品设计与用户体验中心',
    deptId: 105,
    jobTitle: '实习体验设计师',
    bio: '用心感受用户，探索更通用现代的交互语言。',
    gender: '男',
    securityScore: 80,
    enable2FA: false,
    lastLoginTime: '2026-10-19 09:20:15',
    lastLoginIp: '114.242.25.12',
    createdAt: '2024-09-01 15:45:00'
  },
  // Backward compatibility aliases
  {
    id: 'USR-1006',
    username: 'iot_operator',
    realName: '张建国',
    role: 'operation_manager',
    roleName: '业务与运营总监',
    phone: '13912345678',
    email: 'operator@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    department: '运营管理与客户成功中心',
    deptId: 111,
    jobTitle: '运营业务负责人',
    lastLoginTime: '2026-10-20 14:15:22',
    lastLoginIp: '192.168.2.45',
    createdAt: '2024-03-15 14:30:00'
  },
  {
    id: 'USR-1007',
    username: 'test_dev',
    realName: '周子文',
    role: 'tech_developer',
    roleName: '技术开发主管',
    phone: '13788889999',
    email: 'dev@cloudhub-admin.com',
    status: 1,
    avatar: 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
    department: '前端架构与应用研发组',
    deptId: 102,
    jobTitle: '高级研发工程师',
    lastLoginTime: '2026-10-20 13:45:10',
    lastLoginIp: '192.168.1.142',
    createdAt: '2024-06-20 10:15:00'
  }
]

// 4. Initial Universal Assets & Resources (Universal Terminals, Servers, Gateways, IoT)
const INITIAL_DEVICES = [
  {
    id: 'AST-GW-001',
    name: '分布式微服务API接入网关 A-01',
    deviceType: 'gateway',
    typeName: '云端网关节点',
    sn: 'SN-GW-2026-0901',
    protocol: 'MQTT / WebSocket',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/gateway/01',
    clientId: 'cloudhub_edge_gw_01',
    status: 'online',
    ip: '192.168.10.15',
    firmware: 'v2.4.2',
    heartbeatInterval: 60,
    location: '核心数据中心机房 A-03机柜',
    cpuUsage: 32,
    memoryUsage: 45,
    temperature: 36.4,
    rssi: -52,
    msgCountToday: 28450,
    lastHeartbeat: '刚刚 (2秒前)',
    description: '负责跨地域分布式节点请求调度与全协议双向转发'
  },
  {
    id: 'AST-SRV-002',
    name: '微服务生产主集群计算节点 S-02',
    deviceType: 'server',
    typeName: '计算服务器',
    sn: 'SN-SRV-2026-0412',
    protocol: 'HTTP / RESTful',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/server/compute_02',
    clientId: 'compute_node_srv_02',
    status: 'online',
    ip: '192.168.10.22',
    firmware: 'v4.1.2-LTS',
    heartbeatInterval: 30,
    location: '华北一区集群机房 B-08机柜',
    cpuUsage: 42,
    memoryUsage: 58,
    temperature: 38.2,
    rssi: -40,
    msgCountToday: 64120,
    lastHeartbeat: '5秒前',
    description: '承载高并发应用微服务、数据聚合与核心业务逻辑计算'
  },
  {
    id: 'AST-IOT-003',
    name: '机房环境多参数微气候传感仪',
    deviceType: 'sensor',
    typeName: '环境传感设备',
    sn: 'SN-TH-2026-0812',
    protocol: 'MQTT 3.1.1',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/sensors/datacenter_env',
    clientId: 'sensor_env_th_03',
    status: 'online',
    ip: '192.168.10.88',
    firmware: 'v1.3.0',
    heartbeatInterval: 30,
    location: 'IDC主机房 1号温湿度监测点',
    cpuUsage: 12,
    memoryUsage: 22,
    temperature: 22.8,
    rssi: -65,
    msgCountToday: 11200,
    lastHeartbeat: '12秒前',
    description: '24小时不间断环境温度、湿度及微气流采样监测'
  },
  {
    id: 'AST-POS-004',
    name: '智能商用一体化交互终端 POS-08',
    deviceType: 'terminal',
    typeName: '商用智能终端',
    sn: 'SN-POS-2026-0304',
    protocol: 'HTTPS / MQTT',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/terminals/pos_08',
    clientId: 'smart_pos_terminal_08',
    status: 'warning',
    ip: '192.168.12.104',
    firmware: 'v2.0.1',
    heartbeatInterval: 120,
    location: '数字化服务大厅 08号业务窗口',
    cpuUsage: 64,
    memoryUsage: 71,
    temperature: 46.2,
    rssi: -72,
    msgCountToday: 8900,
    lastHeartbeat: '1分钟前 (告警)',
    description: '内置打印模组缺纸且外设扫码枪离线，触发平台维护预警'
  },
  {
    id: 'AST-NET-005',
    name: '核心千兆分布式网络交换机 SW-02',
    deviceType: 'network',
    typeName: '网络基础设施',
    sn: 'SN-SW-2026-0451',
    protocol: 'SNMP / MQTT',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/network/switch_02',
    clientId: 'switch_core_net_02',
    status: 'offline',
    ip: '192.168.10.1',
    firmware: 'v3.5.0',
    heartbeatInterval: 60,
    location: '核心网络配线室 Rack-C',
    cpuUsage: 0,
    memoryUsage: 0,
    temperature: 0,
    rssi: -99,
    msgCountToday: 0,
    lastHeartbeat: '25分钟前 (脱机)',
    description: '冗余辅助链路脱机，系统已平滑切换为主干高可用专线'
  },
  {
    id: 'AST-AI-006',
    name: '边缘AI视觉计算推理工作站 W-05',
    deviceType: 'ai_vision',
    typeName: '算力推理终端',
    sn: 'SN-AI-2026-1109',
    protocol: 'RTSP + gRPC',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/vision/events',
    clientId: 'vision_inference_node_05',
    status: 'online',
    ip: '192.168.10.201',
    firmware: 'v3.2.4',
    heartbeatInterval: 15,
    location: '智能图像质检与安防监控中心',
    cpuUsage: 76,
    memoryUsage: 68,
    temperature: 42.1,
    rssi: -48,
    msgCountToday: 31500,
    lastHeartbeat: '刚刚',
    description: '实时视觉图像流AI推理与多维异常事件结构化上报'
  },
  {
    id: 'AST-AGV-007',
    name: '智能自主移动服务机器人 AGV-03',
    deviceType: 'robot',
    typeName: '移动服务机器人',
    sn: 'SN-AGV-2026-0033',
    protocol: 'MQTT 5.0',
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    topic: 'cloudhub/robot/agv03/telemetry',
    clientId: 'agv_nav_client_03',
    status: 'online',
    ip: '192.168.15.55',
    firmware: 'v4.1.0',
    heartbeatInterval: 5,
    location: '物流中转环线 B区充电站',
    cpuUsage: 44,
    memoryUsage: 52,
    temperature: 31.5,
    rssi: -58,
    msgCountToday: 45800,
    lastHeartbeat: '刚刚',
    description: '激光SLAM自主导航巡航中，当前电量 88%，状态健康'
  }
]

// 5. Initial Universal Data Dictionaries
const INITIAL_DICT_TYPES = [
  {
    id: 1,
    dictName: '用户账号状态',
    dictType: 'sys_user_status',
    status: 1,
    remark: '用户系统账号可用与封禁状态',
    createTime: '2024-01-01 10:00:00'
  },
  {
    id: 2,
    dictName: '资源资产运行状态',
    dictType: 'sys_device_status',
    status: 1,
    remark: '终端、服务器与资产在线、预警与脱机状态',
    createTime: '2024-01-01 10:10:00'
  },
  {
    id: 3,
    dictName: '系统告警级别',
    dictType: 'sys_alert_level',
    status: 1,
    remark: '平台运维告警严重等级分类',
    createTime: '2024-01-05 11:20:00'
  },
  {
    id: 4,
    dictName: '业务工单流转状态',
    dictType: 'sys_order_status',
    status: 1,
    remark: '任务与服务申请流程状态',
    createTime: '2024-01-10 14:00:00'
  },
  {
    id: 5,
    dictName: '网络通信协议类型',
    dictType: 'sys_protocol_type',
    status: 1,
    remark: '微服务网关与终端接口通信协议',
    createTime: '2024-01-15 15:00:00'
  },
  {
    id: 6,
    dictName: '消息通知推送渠道',
    dictType: 'sys_notice_channel',
    status: 1,
    remark: '告警与系统消息多通道分发途径',
    createTime: '2024-01-20 16:30:00'
  }
]

const INITIAL_DICT_DATA = [
  { id: 101, dictType: 'sys_user_status', label: '正常启用', value: '1', listClass: 'success', isDefault: true, orderNum: 1 },
  { id: 102, dictType: 'sys_user_status', label: '锁定禁用', value: '0', listClass: 'danger', isDefault: false, orderNum: 2 },

  { id: 201, dictType: 'sys_device_status', label: '正常运行', value: 'online', listClass: 'success', isDefault: true, orderNum: 1 },
  { id: 202, dictType: 'sys_device_status', label: '指标预警', value: 'warning', listClass: 'warning', isDefault: false, orderNum: 2 },
  { id: 203, dictType: 'sys_device_status', label: '网络脱机', value: 'offline', listClass: 'info', isDefault: false, orderNum: 3 },

  { id: 301, dictType: 'sys_alert_level', label: '提示信息', value: 'info', listClass: 'info', isDefault: false, orderNum: 1 },
  { id: 302, dictType: 'sys_alert_level', label: '一般预警', value: 'warning', listClass: 'warning', isDefault: true, orderNum: 2 },
  { id: 303, dictType: 'sys_alert_level', label: '紧急故障', value: 'danger', listClass: 'danger', isDefault: false, orderNum: 3 },

  { id: 401, dictType: 'sys_order_status', label: '草稿待提交', value: 'draft', listClass: 'info', isDefault: false, orderNum: 1 },
  { id: 402, dictType: 'sys_order_status', label: '审批处理中', value: 'pending', listClass: 'primary', isDefault: true, orderNum: 2 },
  { id: 403, dictType: 'sys_order_status', label: '审批已通过', value: 'approved', listClass: 'success', isDefault: false, orderNum: 3 },
  { id: 404, dictType: 'sys_order_status', label: '流程已驳回', value: 'rejected', listClass: 'danger', isDefault: false, orderNum: 4 },

  { id: 501, dictType: 'sys_protocol_type', label: 'HTTP / RESTful', value: 'http', listClass: 'primary', isDefault: true, orderNum: 1 },
  { id: 502, dictType: 'sys_protocol_type', label: 'MQTT 3.1.1 / 5.0', value: 'mqtt', listClass: 'success', isDefault: false, orderNum: 2 },
  { id: 503, dictType: 'sys_protocol_type', label: 'WebSocket 全双工', value: 'websocket', listClass: 'warning', isDefault: false, orderNum: 3 },
  { id: 504, dictType: 'sys_protocol_type', label: 'gRPC 高性能通信', value: 'grpc', listClass: 'info', isDefault: false, orderNum: 4 },

  { id: 601, dictType: 'sys_notice_channel', label: '站内消息信箱', value: 'in_app', listClass: 'primary', isDefault: true, orderNum: 1 },
  { id: 602, dictType: 'sys_notice_channel', label: '电子邮件推送', value: 'email', listClass: 'success', isDefault: false, orderNum: 2 },
  { id: 603, dictType: 'sys_notice_channel', label: '钉钉群机器人', value: 'dingtalk', listClass: 'warning', isDefault: false, orderNum: 3 },
  { id: 604, dictType: 'sys_notice_channel', label: '企业微信机器人', value: 'wecom', listClass: 'info', isDefault: false, orderNum: 4 }
]

// 6. Initial Universal Platform Settings
const INITIAL_SETTINGS = {
  general: {
    siteName: 'FastVue-Admin 企业级通用管理平台',
    siteSubTitle: 'Universal Modern Operations & Management Platform',
    recordNo: '京ICP备2026102008号-1',
    adminEmail: 'service@fastvue-admin.com',
    companyName: 'FastVue-Admin 数字化创新实验室',
    copyright: '© 2026 FastVue-Admin Team. 保留所有权利',
    autoRefreshInterval: 15,
    language: 'zh-CN',
    theme: 'light'
  },
  mqtt: {
    brokerIp: '8.163.51.74',
    brokerPort: 9003,
    clientIdPrefix: 'cloudhub_admin_gateway_',
    keepalive: 60,
    cleanSession: true,
    defaultTopic: 'cloudhub/broadcast/event',
    qos: 1,
    username: 'cloudhub_admin',
    password: '••••••••',
    enableSsl: false,
    retryCount: 5,
    reconnectPeriod: 5000
  },
  security: {
    minPasswordLength: 8,
    requireSpecialChars: true,
    requireNumbersAndLetters: true,
    maxLoginFailAttempts: 5,
    lockoutDurationMinutes: 15,
    sessionTimeoutMinutes: 60,
    enable2FA: false,
    ipWhitelist: '192.168.1.0/24, 10.0.0.0/16, 127.0.0.1'
  },
  notification: {
    enableEmailAlerts: true,
    emailRecipients: 'ops-alerts@cloudhub-admin.com',
    enableDingTalk: true,
    dingTalkWebhook: 'https://oapi.dingtalk.com/robot/send?access_token=cloudhub_demo_key',
    deviceOfflineAlertTime: 180,
    warningAlertThreshold: 45
  }
}

// 7. Initial Universal Audit Logs
const INITIAL_LOGS = [
  {
    id: 1,
    time: '2026-10-20 15:30:10',
    operator: 'admin',
    action: '用户登录',
    target: '统一SSO安全身份鉴权中心',
    detail: '超级系统管理员通过 Web 控制台安全登录，角色【超级系统管理员】',
    status: 'success',
    ip: '192.168.1.108'
  },
  {
    id: 2,
    time: '2026-10-20 15:12:05',
    operator: 'admin',
    action: '下发控制指令',
    target: 'AST-GW-001',
    detail: '下发分布式微服务集群同步指令，topic: cloudhub/gateway/01, payload: {"cmd":"sync_all"}',
    status: 'success',
    ip: '192.168.1.108'
  },
  {
    id: 3,
    time: '2026-10-20 14:45:10',
    operator: 'developer',
    action: '更新数据字典',
    target: 'sys_protocol_type',
    detail: '新增协议支持类型: gRPC 高性能通信规范',
    status: 'success',
    ip: '192.168.1.142'
  },
  {
    id: 4,
    time: '2026-10-20 14:15:22',
    operator: 'operator',
    action: '组织架构维护',
    target: '产品设计与用户体验中心',
    detail: '调整组织架构部门负责人为【张雅婷】',
    status: 'success',
    ip: '192.168.2.45'
  },
  {
    id: 5,
    time: '2026-10-20 13:20:00',
    operator: 'SYSTEM',
    action: '终端设备告警',
    target: 'AST-POS-004',
    detail: '智能商用终端缺纸传感器触发黄色预警，已分派运维核查',
    status: 'warning',
    ip: '127.0.0.1'
  }
]

// 8. Server & Infrastructure Monitor Status
export function getSystemMonitorMetrics() {
  return {
    cpu: {
      usage: 28.4,
      cores: 8,
      model: 'Apple M-Series / High-Performance 8-Core',
      frequency: '3.2 GHz'
    },
    memory: {
      total: '16.0 GB',
      used: '7.8 GB',
      free: '8.2 GB',
      usage: 48.7
    },
    disk: {
      total: '512.0 GB',
      used: '198.4 GB',
      free: '313.6 GB',
      usage: 38.8
    },
    system: {
      os: 'macOS Darwin (arm64) / Cloud Universal Ready',
      nodeVersion: 'v24.22.0',
      uptime: '14 天 6 小时 32 分钟',
      serverTime: new Date().toLocaleString('zh-CN', { hour12: false })
    },
    services: [
      { name: 'API 网关服务 (Cloud Gateway)', status: 'online', port: 8080, latency: '8ms', reqCount: '1,420,890' },
      { name: '用户鉴权与SSO中心', status: 'online', port: 8081, latency: '12ms', reqCount: '584,200' },
      { name: '分布式通信数据代理 (Broker)', status: 'online', port: 9003, latency: '11ms', reqCount: '3,850,110' },
      { name: 'PostgreSQL 主数据库集群', status: 'online', port: 5432, latency: '4ms', reqCount: '2,980,450' },
      { name: 'Redis 高性能缓存队列', status: 'online', port: 6379, latency: '1ms', reqCount: '9,450,200' },
      { name: '时序遥测数据库 (TSDB)', status: 'online', port: 8086, latency: '15ms', reqCount: '7,120,400' }
    ]
  }
}

// Storage helpers with graceful upgrade/migration
export function getStoredDepartments() {
  const data = localStorage.getItem('ent_departments_data')
  if (!data) {
    localStorage.setItem('ent_departments_data', JSON.stringify(INITIAL_DEPARTMENTS))
    return INITIAL_DEPARTMENTS
  }
  const parsed = JSON.parse(data)
  // Auto-upgrade if legacy department name
  if (parsed[0]?.deptName?.includes('智企')) {
    localStorage.setItem('ent_departments_data', JSON.stringify(INITIAL_DEPARTMENTS))
    return INITIAL_DEPARTMENTS
  }
  return parsed
}

export function saveStoredDepartments(depts) {
  localStorage.setItem('ent_departments_data', JSON.stringify(depts))
}

export function getStoredRoles() {
  const data = localStorage.getItem('ent_roles_data')
  if (!data) {
    localStorage.setItem('ent_roles_data', JSON.stringify(INITIAL_ROLES))
    return INITIAL_ROLES
  }
  return JSON.parse(data)
}

export function saveStoredRoles(roles) {
  localStorage.setItem('ent_roles_data', JSON.stringify(roles))
}

export function getStoredDictTypes() {
  const data = localStorage.getItem('ent_dict_types_data')
  if (!data) {
    localStorage.setItem('ent_dict_types_data', JSON.stringify(INITIAL_DICT_TYPES))
    return INITIAL_DICT_TYPES
  }
  const parsed = JSON.parse(data)
  // Ensure new universal dict types are present
  if (parsed.length < INITIAL_DICT_TYPES.length) {
    localStorage.setItem('ent_dict_types_data', JSON.stringify(INITIAL_DICT_TYPES))
    return INITIAL_DICT_TYPES
  }
  return parsed
}

export function saveStoredDictTypes(types) {
  localStorage.setItem('ent_dict_types_data', JSON.stringify(types))
}

export function getStoredDictData() {
  const data = localStorage.getItem('ent_dict_items_data')
  if (!data) {
    localStorage.setItem('ent_dict_items_data', JSON.stringify(INITIAL_DICT_DATA))
    return INITIAL_DICT_DATA
  }
  const parsed = JSON.parse(data)
  if (parsed.length < INITIAL_DICT_DATA.length) {
    localStorage.setItem('ent_dict_items_data', JSON.stringify(INITIAL_DICT_DATA))
    return INITIAL_DICT_DATA
  }
  return parsed
}

export function saveStoredDictData(items) {
  localStorage.setItem('ent_dict_items_data', JSON.stringify(items))
}

export function getStoredUsers() {
  const data = localStorage.getItem('ent_users_data')
  if (!data) {
    localStorage.setItem('ent_users_data', JSON.stringify(INITIAL_USERS))
    return INITIAL_USERS
  }
  const parsed = JSON.parse(data)
  // Auto-upgrade if using legacy department names
  if (parsed[0]?.department?.includes('智企') || !parsed.some(u => u.username === 'operator')) {
    localStorage.setItem('ent_users_data', JSON.stringify(INITIAL_USERS))
    return INITIAL_USERS
  }
  return parsed
}

export function saveStoredUsers(users) {
  localStorage.setItem('ent_users_data', JSON.stringify(users))
}

export function getStoredDevices() {
  const data = localStorage.getItem('ent_devices_data')
  if (!data) {
    localStorage.setItem('ent_devices_data', JSON.stringify(INITIAL_DEVICES))
    return INITIAL_DEVICES
  }
  const parsed = JSON.parse(data)
  // Upgrade if legacy devices exist
  if (!parsed.some(d => d.id === 'AST-SRV-002' || d.id === 'AST-GW-001')) {
    localStorage.setItem('ent_devices_data', JSON.stringify(INITIAL_DEVICES))
    return INITIAL_DEVICES
  }
  return parsed
}

export function saveStoredDevices(devices) {
  localStorage.setItem('ent_devices_data', JSON.stringify(devices))
}

export function getStoredSettings() {
  const data = localStorage.getItem('ent_settings_data')
  if (!data) {
    localStorage.setItem('ent_settings_data', JSON.stringify(INITIAL_SETTINGS))
    return INITIAL_SETTINGS
  }
  const parsed = JSON.parse(data)
  // Auto-upgrade if using legacy title
  if (parsed.general?.siteName?.includes('智企') || parsed.general?.siteName?.includes('智联')) {
    parsed.general.siteName = INITIAL_SETTINGS.general.siteName
    parsed.general.siteSubTitle = INITIAL_SETTINGS.general.siteSubTitle
    parsed.general.companyName = INITIAL_SETTINGS.general.companyName
    parsed.general.copyright = INITIAL_SETTINGS.general.copyright
    localStorage.setItem('ent_settings_data', JSON.stringify(parsed))
  }
  return parsed
}

export function saveStoredSettings(settings) {
  localStorage.setItem('ent_settings_data', JSON.stringify(settings))
}

export function getStoredLogs() {
  const data = localStorage.getItem('ent_logs_data')
  if (!data) {
    localStorage.setItem('ent_logs_data', JSON.stringify(INITIAL_LOGS))
    return INITIAL_LOGS
  }
  const parsed = JSON.parse(data)
  if (parsed[0]?.target?.includes('AST-SRV-001') && parsed[0]?.detail?.includes('enterprise')) {
    localStorage.setItem('ent_logs_data', JSON.stringify(INITIAL_LOGS))
    return INITIAL_LOGS
  }
  return parsed
}

// 6. Initial Platform Members / Registered End Users (用户管理 - 业务/平台端会员与注册用户)
export const INITIAL_MEMBERS = [
  {
    id: 'UID-800101',
    username: 'geek_chen',
    nickname: '极客先锋',
    realName: '陈子涵',
    phone: '13812345678',
    email: 'chen.zihan@outlook.com',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    memberLevel: 'diamond', // regular, silver, gold, diamond
    points: 86400,
    balance: 5240.00,
    channel: 'web', // web, app, wechat, open_api
    verifyStatus: 1, // 1: 已实名, 0: 未实名, 2: 审核中
    status: 1, // 1: 正常, 0: 冻结
    tags: ['核心客户', '高频活跃', '月度消费TOP'],
    idCard: '310104********2819',
    registerTime: '2024-02-18 10:25:30',
    lastActiveTime: '2026-10-20 15:42:10',
    loginCount: 342,
    remark: '平台早期种子钻石客户，主要通过Web后台调用开放平台API'
  },
  {
    id: 'UID-800102',
    username: 'star_walker',
    nickname: '星海漫步',
    realName: '林依依',
    phone: '15921887654',
    email: 'lin.yiyi@gmail.com',
    avatar: 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
    memberLevel: 'gold',
    points: 34200,
    balance: 1850.50,
    channel: 'app',
    verifyStatus: 1,
    status: 1,
    tags: ['移动端活跃', '金牌会员'],
    idCard: '110101********3920',
    registerTime: '2024-05-10 14:12:00',
    lastActiveTime: '2026-10-20 14:20:05',
    loginCount: 188,
    remark: '主要使用移动端App进行设备订阅与告警消息接收'
  },
  {
    id: 'UID-800103',
    username: 'sunrise_glow',
    nickname: '晨曦微光',
    realName: '赵天成',
    phone: '18610023456',
    email: 'zhao.tc@163.com',
    avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    memberLevel: 'silver',
    points: 12500,
    balance: 380.00,
    channel: 'wechat',
    verifyStatus: 1,
    status: 1,
    tags: ['小程序用户', '白银会员'],
    idCard: '440301********1102',
    registerTime: '2024-08-22 09:30:18',
    lastActiveTime: '2026-10-19 19:15:33',
    loginCount: 95,
    remark: '微信小程序注册，日常通过移动端轻量审批与查看报表'
  },
  {
    id: 'UID-800104',
    username: 'quantum_leap',
    nickname: '量子飞跃',
    realName: '孙梦洁',
    phone: '13799887766',
    email: 'sun.mj@qq.com',
    avatar: 'https://cube.elemecdn.com/2/3a/057d60ff3123896541f4864c3c399png.png',
    memberLevel: 'diamond',
    points: 128900,
    balance: 16800.00,
    channel: 'open_api',
    verifyStatus: 1,
    status: 1,
    tags: ['企业签约', 'API接入', 'KA大客户'],
    idCard: '330106********4412',
    registerTime: '2024-01-05 11:00:20',
    lastActiveTime: '2026-10-20 16:01:25',
    loginCount: 520,
    remark: '企业开发者大客户，月均接口调用量超100万次'
  },
  {
    id: 'UID-800105',
    username: 'cloud_architect',
    nickname: '云上行者',
    realName: '周伟明',
    phone: '15011223344',
    email: 'zhou.wm@aliyun.com',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    memberLevel: 'regular',
    points: 2100,
    balance: 0.00,
    channel: 'web',
    verifyStatus: 2, // 审核中
    status: 1,
    tags: ['新注册', '实名审核中'],
    idCard: '420102********5518',
    registerTime: '2026-10-15 16:40:10',
    lastActiveTime: '2026-10-20 11:22:45',
    loginCount: 14,
    remark: '近期新注册用户，提交了企业实名认证材料等待平台审核'
  },
  {
    id: 'UID-800106',
    username: 'smart_commerce',
    nickname: '智汇商联',
    realName: '吴雅楠',
    phone: '13366778899',
    email: 'wu.yn@commerce.cn',
    avatar: 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
    memberLevel: 'gold',
    points: 46700,
    balance: 2450.00,
    channel: 'web',
    verifyStatus: 1,
    status: 0, // 冻结
    tags: ['异常登录', '风控冻结'],
    idCard: '320106********0921',
    registerTime: '2024-06-18 13:10:00',
    lastActiveTime: '2026-10-18 22:10:00',
    loginCount: 140,
    remark: '检测到异地高频异常IP爆破登录，触发系统安全风控策略自动临时冻结'
  },
  {
    id: 'UID-800107',
    username: 'nebula_light',
    nickname: '星云微光',
    realName: '郑家豪',
    phone: '18955667788',
    email: 'zheng.jh@foxmail.com',
    avatar: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    memberLevel: 'silver',
    points: 8900,
    balance: 120.00,
    channel: 'app',
    verifyStatus: 0, // 未实名
    status: 1,
    tags: ['移动端', '待实名'],
    idCard: '',
    registerTime: '2026-09-02 15:20:10',
    lastActiveTime: '2026-10-19 18:30:12',
    loginCount: 38,
    remark: '普通个人移动端用户，尚未完成二代身份证实名认证'
  }
]

// 7. Initial Equipment / Hardware Devices (设备管理 - 实体终端硬件/物联设备/智能设备台账)
export const INITIAL_EQUIPMENTS = [
  {
    id: 'EQP-1001',
    name: '智能商用交互结算一体机-01',
    deviceCode: 'POS-SH-2026-001',
    category: 'terminal', // terminal, sensor, gateway, ai_camera, robot, pda
    categoryName: '智能商用终端',
    model: 'SmartPOS-Ultra Pro-X8',
    macAddress: '00:1B:44:11:3A:B7',
    ip: '192.168.10.101',
    networkType: '5G 全网通 + Wi-Fi 6',
    signalLevel: 5, // 1 - 5
    status: 'running', // running, standby, warning, offline
    powerStatus: true,
    firmwareVersion: 'v2.8.4-build2026',
    cpuLoad: 28,
    memoryLoad: 42,
    temperature: 36.8,
    battery: 100,
    location: '华东旗舰展厅 智慧收银区A-01',
    lastHeartbeat: '2026-10-20 16:08:12',
    onlineDuration: '28天 14小时',
    description: '搭载多点触控与人脸生物核验识别的高可靠商用结算一体终端'
  },
  {
    id: 'EQP-1002',
    name: '机房高精度微气候温湿度传感仪',
    deviceCode: 'ENV-IDC-2026-002',
    category: 'sensor',
    categoryName: '环境传感设备',
    model: 'SensClim-IoT-T80',
    macAddress: '3C:52:82:7D:E4:10',
    ip: '192.168.10.102',
    networkType: '工业级千兆以太网',
    signalLevel: 5,
    status: 'running',
    powerStatus: true,
    firmwareVersion: 'v1.4.12',
    cpuLoad: 12,
    memoryLoad: 25,
    temperature: 24.2,
    battery: 100,
    location: '主数据中心 IDC机房B区04机柜',
    lastHeartbeat: '2026-10-20 16:08:40',
    onlineDuration: '142天 06小时',
    description: '工业级双通道高精度微环境传感单元，支持毫秒级温湿度与烟雾监测'
  },
  {
    id: 'EQP-1003',
    name: '分布式边缘计算智能工业微网关',
    deviceCode: 'GW-EDGE-2026-003',
    category: 'gateway',
    categoryName: '边缘智能网关',
    model: 'EdgeGate-Arm64-G5',
    macAddress: '70:B3:D5:E2:8F:99',
    ip: '192.168.10.103',
    networkType: '5G 双卡双待冗余',
    signalLevel: 4,
    status: 'warning',
    powerStatus: true,
    firmwareVersion: 'v3.1.0-rc2',
    cpuLoad: 88,
    memoryLoad: 82,
    temperature: 68.5,
    battery: 92,
    location: '智能园区变电站 动力监控配电柜',
    lastHeartbeat: '2026-10-20 16:07:55',
    onlineDuration: '12天 09小时',
    description: '网关当前CPU与温升较高，正在高并发汇聚下游48个传感器节点报文'
  },
  {
    id: 'EQP-1004',
    name: 'AI边缘视觉检测推理工作站-C3',
    deviceCode: 'AI-VIS-2026-004',
    category: 'ai_camera',
    categoryName: 'AI视觉终端',
    model: 'VisionAI-NPU-64T',
    macAddress: 'B8:27:EB:4F:91:2C',
    ip: '192.168.10.104',
    networkType: '工业级千兆以太网',
    signalLevel: 5,
    status: 'running',
    powerStatus: true,
    firmwareVersion: 'v4.0.2',
    cpuLoad: 64,
    memoryLoad: 58,
    temperature: 48.0,
    battery: 100,
    location: '智能制造流水线 质检工位C-03',
    lastHeartbeat: '2026-10-20 16:08:29',
    onlineDuration: '45天 18小时',
    description: '配备双目高帧率工业摄像头与64TOPS边缘神经网络算力，实时检测外观缺陷'
  },
  {
    id: 'EQP-1005',
    name: '园区自主导航巡检服务机器人-02',
    deviceCode: 'ROB-NAV-2026-005',
    category: 'robot',
    categoryName: '移动巡检终端',
    model: 'PatrolBot-NavSLAM-M3',
    macAddress: 'DC:A6:32:1A:67:3E',
    ip: '192.168.10.105',
    networkType: '5G 专网无线切片',
    signalLevel: 4,
    status: 'standby',
    powerStatus: true,
    firmwareVersion: 'v2.2.5',
    cpuLoad: 18,
    memoryLoad: 32,
    temperature: 32.4,
    battery: 45,
    location: '研发园区 1号科研楼大堂充电桩',
    lastHeartbeat: '2026-10-20 16:08:02',
    onlineDuration: '3天 02小时',
    description: '激光雷达自主导航移动底盘，正处于底座自动回充与待机待命巡检状态'
  },
  {
    id: 'EQP-1006',
    name: '智能仓储移动手持扫码PDA终端',
    deviceCode: 'PDA-LOG-2026-006',
    category: 'pda',
    categoryName: '手持手持终端',
    model: 'HandScan-Rugged-H6',
    macAddress: 'F0:18:98:23:CD:45',
    ip: '192.168.10.106',
    networkType: 'Wi-Fi 6 双频',
    signalLevel: 0,
    status: 'offline',
    powerStatus: false,
    firmwareVersion: 'v1.8.9',
    cpuLoad: 0,
    memoryLoad: 0,
    temperature: 0,
    battery: 12,
    location: '物流中转立体仓库 拣货分拣区3号台',
    lastHeartbeat: '2026-10-20 11:45:00',
    onlineDuration: '离线',
    description: '终端电池电量耗尽且处于关机脱机状态，等待进入充电柜补充电量'
  }
]

export function getStoredMembers() {
  const data = localStorage.getItem('hub_members_data')
  if (!data) {
    localStorage.setItem('hub_members_data', JSON.stringify(INITIAL_MEMBERS))
    return INITIAL_MEMBERS
  }
  return JSON.parse(data)
}

export function saveStoredMembers(members) {
  localStorage.setItem('hub_members_data', JSON.stringify(members))
}

export function getStoredEquipments() {
  const data = localStorage.getItem('hub_equipments_data')
  if (!data) {
    localStorage.setItem('hub_equipments_data', JSON.stringify(INITIAL_EQUIPMENTS))
    return INITIAL_EQUIPMENTS
  }
  return JSON.parse(data)
}

export function saveStoredEquipments(equipments) {
  localStorage.setItem('hub_equipments_data', JSON.stringify(equipments))
}

export function addAuditLog(entry) {
  const logs = getStoredLogs()
  const newLog = {
    id: Date.now(),
    time: new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-'),
    ...entry
  }
  logs.unshift(newLog)
  localStorage.setItem('ent_logs_data', JSON.stringify(logs.slice(0, 50)))
}
