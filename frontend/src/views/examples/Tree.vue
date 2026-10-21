<template>
  <PageContainer
    title="树形列表"
    description="适用于分类、栏目、目录等层级数据。示例展示树形表格与可过滤目录。"
  >
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card shadow="never">
          <el-input v-model="keyword" placeholder="筛选目录" clearable class="starter-gap" />
          <el-tree
            ref="tree"
            :data="data"
            node-key="id"
            default-expand-all
            :filter-node-method="filter"
            :props="{ label: 'name' }"
          />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="16">
        <el-card shadow="never">
          <el-table :data="data" row-key="id" default-expand-all>
            <el-table-column prop="name" label="名称" min-width="180" />
            <el-table-column prop="key" label="标识" min-width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }"><StatusTag :value="row.status" /></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </PageContainer>
</template>
<script setup>
import { ref, watch } from 'vue'
import PageContainer from '@/components/admin/PageContainer.vue'
import StatusTag from '@/components/admin/StatusTag.vue'
const keyword = ref(''),
  tree = ref()
const data = [
  {
    id: 1,
    name: '示例目录',
    key: 'root',
    status: 1,
    children: [
      {
        id: 2,
        name: '基础分类',
        key: 'basic',
        status: 1,
        children: [{ id: 3, name: '子分类', key: 'child', status: 1 }],
      },
      { id: 4, name: '归档分类', key: 'archive', status: 0 },
    ],
  },
]
const filter = (value, node) => !value || node.name.includes(value)
watch(keyword, (value) => tree.value?.filter(value))
</script>
