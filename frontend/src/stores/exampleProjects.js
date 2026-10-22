import { defineStore } from 'pinia'

export const projectTypes = ['产品研发', '运营活动', '内部建设']
export const projectTeams = {
  产品研发: ['林晓', '陈雨'],
  运营活动: ['周宁', '李悦'],
  内部建设: ['林晓', '周宁'],
}
export const projectStates = {
  planned: { label: '待启动', type: 'info' },
  active: { label: '进行中', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
}
const names = [
  '客户服务门户',
  '移动端体验优化',
  '季度品牌活动',
  '知识库建设',
  '数据分析平台',
  '成员培训计划',
  '开放接口接入',
  '用户增长实验',
  '资产管理升级',
  '反馈中心改版',
  '内容运营计划',
  '协作流程优化',
]
const createProjects = () =>
  names.map((name, index) => ({
    id: `project-${index + 1}`,
    code: `PRJ-${String(index + 1).padStart(3, '0')}`,
    name,
    category: projectTypes[index % 3],
    owner: projectTeams[projectTypes[index % 3]][index % 2],
    status: ['active', 'planned', 'completed'][index % 3],
    progress: index % 3 === 2 ? 100 : index % 3 === 1 ? 0 : 35 + index * 4,
    dates: ['2026-10-01', '2026-12-31'],
    budget: (index + 1) * 5000,
    description: `${name}的阶段目标、交付内容与团队协作安排。`,
    createdAt: '2026-10-01 09:00',
    updatedAt: '2026-10-01 09:00',
    events: [{ time: '2026-10-01 09:00', text: '创建项目' }],
  }))

// Deliberately isolated from real business APIs; shared across example pages until refresh.
export const useExampleProjects = defineStore('example-projects', {
  state: () => ({ projects: createProjects() }),
  actions: {
    save(input) {
      const duplicate = this.projects.some((p) => p.code === input.code && p.id !== input.id)
      if (duplicate) throw new Error('项目编号已存在')
      const time = new Date().toLocaleString('zh-CN', { hour12: false })
      const existing = this.projects.find((p) => p.id === input.id)
      const data = { ...input, dates: [...input.dates], updatedAt: time }
      if (existing) {
        Object.assign(existing, data)
        existing.events.unshift({ time, text: '更新项目资料' })
        return existing
      }
      const project = {
        ...data,
        id: crypto.randomUUID(),
        createdAt: time,
        events: [{ time, text: '创建项目' }],
      }
      this.projects.unshift(project)
      return project
    },
    remove(ids) {
      this.projects = this.projects.filter((p) => !ids.includes(p.id))
    },
  },
})
