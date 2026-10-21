<template>
  <PageContainer
    title="菜单配置"
    description="查看当前构建启用的路由、分组和权限。菜单由同一份模块配置生成。"
  >
    <el-card shadow="never">
      <el-alert
        title="在 src/config/modules.js 中新增或修改菜单；此页为配置预览，不会将临时编辑伪装成持久配置。"
        type="info"
        :closable="false"
        show-icon
        class="starter-gap"
      />
      <el-table :data="modules" stripe>
        <el-table-column prop="title" label="菜单名称" min-width="140" />
        <el-table-column prop="group" label="分组" min-width="120" />
        <el-table-column prop="path" label="路由地址" min-width="180" />
        <el-table-column prop="permission" label="访问权限" min-width="240">
          <template #default="{ row }">
            <code>{{ row.permission || '登录后可访问' }}</code>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { modules } from '@/config/modules'
import PageContainer from '@/components/admin/PageContainer.vue'
</script>
