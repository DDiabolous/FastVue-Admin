# 实战教程：从零开发“公告管理”功能

本教程以中后台最常见的**“系统公告管理 (Notice Management)”**为例，带你完整走通 FastVue-Admin 的真实前后端二次开发闭环。

通过本教程，你将掌握与当前项目架构完全一致的规范实践：
1. **数据库层**：定义继承 `Record, Base` 的 SQLAlchemy ORM 实体，并生成 Alembic 迁移；
2. **后端服务层**：编写 Pydantic Schema、基于 `app.api.v1.admin.dependencies` 的 `require` 鉴权与 CRUD 路由；
3. **路由注册**：在 `backend/app/api/v1/router.py` 中挂载版本化路由；
4. **前端接口层**：使用项目原生的 `request(path, options)` 封装 API 并获取解包数据；
5. **前端交互层**：利用 `PageContainer`、`FilterPanel`（遵循 `:model` 契约）、`StatusTag` 及 `v-auth` 快速搭建列表与弹窗表单。

---

## 业务需求分析

公告模块包含字段：
- `id`（UUID 字符串，继承自 `Record`）
- `title`（标题，最长 128 字）
- `type`（类型：`notice` 普通通知 / `bulletin` 重大通告 / `alert` 紧急通报）
- `content`（正文内容）
- `status`（发布状态：`draft` 草稿 / `published` 已发布）
- `priority`（优先级：`low` 普通 / `high` 紧急）
- `creator`（创建人账号）
- `createdAt`（创建时间，继承自 `Record`）

权限码定义：
- `system:notice:read`（查看列表与详情）
- `system:notice:create`（新建公告）
- `system:notice:update`（修改与发布）
- `system:notice:delete`（删除公告）

---

## 第一步：后端数据库建模与 Alembic 迁移

### 1. 声明 ORM 模型
在 `backend/app/models/` 目录下新建 `backend/app/models/notice.py`（或追加至 `models` 模块）：

```python
from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class Notice(Record, Base):
    __tablename__ = 'notices'

    title: Mapped[str] = mapped_column(String(128), index=True)
    type: Mapped[str] = mapped_column(String(32), default='notice')
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default='draft', index=True)
    priority: Mapped[str] = mapped_column(String(16), default='normal')
    creator: Mapped[str] = mapped_column(String(64), default='')

    __table_args__ = (Index('ix_notices_status_created', 'status', 'createdAt'),)
```

在 `backend/app/models/__init__.py` 中导出 `Notice`：
```python
from .notice import Notice
```

### 2. 编写 Alembic 迁移脚本
创建 `backend/alembic/versions/0003_create_notices_table.py`：

```python
"""create notices table

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-22 10:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('type', sa.String(length=32), server_default='notice', nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=16), server_default='draft', nullable=False),
        sa.Column('priority', sa.String(length=16), server_default='normal', nullable=False),
        sa.Column('creator', sa.String(length=64), server_default='', nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notices_title', 'notices', ['title'], unique=False)
    op.create_index('ix_notices_status', 'notices', ['status'], unique=False)
    op.create_index('ix_notices_status_created', 'notices', ['status', 'createdAt'], unique=False)


def downgrade():
    op.drop_index('ix_notices_status_created', table_name='notices')
    op.drop_index('ix_notices_status', table_name='notices')
    op.drop_index('ix_notices_title', table_name='notices')
    op.drop_table('notices')
```

在 `backend/` 目录下执行迁移：
```bash
uv run alembic upgrade head
```

---

## 第二步：后端 API 开发与权限挂载

### 1. 编写 Pydantic 数据验证 Schema
新建 `backend/app/schemas/notice.py`：

```python
from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.common import Input, RecordOutput

NoticeType = Literal['notice', 'bulletin', 'alert']
NoticeStatus = Literal['draft', 'published']
NoticePriority = Literal['low', 'normal', 'high']


class NoticeCreate(Input):
    title: str = Field(min_length=2, max_length=128)
    type: NoticeType = 'notice'
    content: str = Field(min_length=1)
    status: NoticeStatus = 'draft'
    priority: NoticePriority = 'normal'


class NoticeUpdate(Input):
    title: str | None = Field(default=None, min_length=2, max_length=128)
    type: NoticeType | None = None
    content: str | None = None
    status: NoticeStatus | None = None
    priority: NoticePriority | None = None


class NoticeRead(RecordOutput):
    title: str
    type: str
    content: str
    status: str
    priority: str
    creator: str
```

### 2. 编写 API 路由
新建 `backend/app/api/v1/admin/notices.py`：

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.api.v1.admin.dependencies import get_current_admin, get_db, require
from app.core.errors import AppError
from app.core.responses import ok
from app.models.notice import Notice
from app.schemas.common import Envelope, PageResult
from app.schemas.notice import NoticeCreate, NoticeRead, NoticeUpdate

router = APIRouter(prefix='/admin/notices', tags=['v1 · 公告管理'])


@router.get(
    '',
    response_model=Envelope[PageResult[NoticeRead]],
    dependencies=[Depends(require('system:notice:read'))],
)
async def list_notices(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    title: str | None = None,
    status: str | None = None,
    db=Depends(get_db),
):
    stmt = select(Notice)
    if title:
        stmt = stmt.where(Notice.title.icontains(title, autoescape=True))
    if status:
        stmt = stmt.where(Notice.status == status)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = (
        await db.scalars(
            stmt.order_by(Notice.createdAt.desc())
            .offset((page - 1) * pageSize)
            .limit(pageSize)
        )
    ).all()
    return ok({'list': rows, 'total': total})


@router.post(
    '',
    response_model=Envelope[NoticeRead],
    dependencies=[Depends(require('system:notice:create'))],
)
async def create_notice(body: NoticeCreate, principal=Depends(get_current_admin), db=Depends(get_db)):
    notice = Notice(**body.model_dump(), creator=principal.user.username)
    db.add(notice)
    await db.commit()
    await db.refresh(notice)
    return ok(notice)


@router.patch(
    '/{id}',
    response_model=Envelope[NoticeRead],
    dependencies=[Depends(require('system:notice:update'))],
)
async def update_notice(id: str, body: NoticeUpdate, db=Depends(get_db)):
    notice = await db.get(Notice, id)
    if not notice:
        raise AppError(404, '公告不存在')
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(notice, key, value)
    await db.commit()
    await db.refresh(notice)
    return ok(notice)


@router.delete(
    '/{id}',
    response_model=Envelope[None],
    dependencies=[Depends(require('system:notice:delete'))],
)
async def delete_notice(id: str, db=Depends(get_db)):
    notice = await db.get(Notice, id)
    if not notice:
        raise AppError(404, '公告不存在')
    await db.delete(notice)
    await db.commit()
    return ok()
```

### 3. 注册子路由
在 `backend/app/api/v1/admin/router.py` 中引入并挂载：

```python
from . import notices

# 在 admin/router.py 中添加：
router.include_router(notices.router)
```

---

## 第三步：前端 API 封装与菜单权限注册

### 1. 封装请求方法
新建 `frontend/src/api/notice.js`（使用项目原生 `request(path, options)` 风格）：

```javascript
import { request } from './adminRequest.js'

export const noticeApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([_, v]) => v !== undefined && v !== '' && v !== null),
    ).toString()
    return request(`/admin/notices${query ? `?${query}` : ''}`)
  },
  create: (body) => request('/admin/notices', { method: 'POST', body }),
  update: (id, body) => request(`/admin/notices/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  remove: (id) => request(`/admin/notices/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
```

> **注意**：项目的 `request.js` 在响应为 200 时会自动解包返回 `result.data`，无需在业务层重复读取 `.data`。

### 2. 注册模块与路由
在 `frontend/src/config/modules.js` 的 `modules` 数组中添加：

```javascript
{
  path: '/system/notices',
  name: 'SystemNotices',
  title: '公告管理',
  group: '系统管理',
  icon: 'Bell',
  permission: 'system:notice:read',
  component: () => import('@/views/system/Notice.vue'),
}
```

并在 `frontend/src/config/permissions.js` 的权限字典中添加权限描述项，供角色管理勾选授权。

---

## 第四步：Vue 3 页面实现

新建 `frontend/src/views/system/Notice.vue`：

```vue
<template>
  <PageContainer title="公告管理" description="维护系统全局通知公告。">
    <!-- 筛选面板：遵循 FilterPanel 规范传入 :model -->
    <FilterPanel :model="filters" @search="loadData">
      <el-form-item label="标题">
        <el-input
          v-model="filters.title"
          placeholder="搜索公告标题"
          clearable
          @keyup.enter="loadData"
        />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="loadData">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
        <el-button
          v-auth="'system:notice:create'"
          type="success"
          icon="Plus"
          @click="openDialog('create')"
        >
          新建公告
        </el-button>
      </template>
    </FilterPanel>

    <!-- 表格区域 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="tableData" v-loading="loading" row-key="id">
        <el-table-column prop="title" label="公告标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'alert'" type="danger">紧急通报</el-tag>
            <el-tag v-else-if="row.type === 'bulletin'" type="warning">重大通告</el-tag>
            <el-tag v-else type="info">普通通知</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <!-- 演示规范的 StatusTag 契约用法 -->
            <StatusTag :value="row.status === 'published' ? 1 : 0" />
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="发布人" width="120" />
        <el-table-column prop="createdAt" label="发布时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-auth="'system:notice:update'"
              link
              type="primary"
              @click="openDialog('update', row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除该条公告吗？"
              confirm-button-text="删除"
              cancel-button-text="取消"
              confirm-button-type="danger"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button v-auth="'system:notice:delete'" link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <div class="pagination-box">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 编辑/新建弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建公告' : '编辑公告'"
      width="640px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio value="notice">普通通知</el-radio>
            <el-radio value="bulletin">重大通告</el-radio>
            <el-radio value="alert">紧急通报</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="form.status"
            active-value="published"
            inactive-value="draft"
            active-text="直接发布"
            inactive-text="存为草稿"
          />
        </el-form-item>
        <el-form-item label="正文" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            placeholder="请输入正文内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageContainer from '@/components/admin/PageContainer.vue'
import FilterPanel from '@/components/admin/FilterPanel.vue'
import StatusTag from '@/components/admin/StatusTag.vue'
import { noticeApi } from '@/api/notice.js'

const loading = ref(false)
const tableData = ref([])
const filters = reactive({ title: '', status: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const currentId = ref(null)
const formRef = ref(null)

const form = reactive({
  title: '',
  type: 'notice',
  status: 'draft',
  content: '',
})

const formRules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入正文内容', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    const data = await noticeApi.list({
      page: pagination.page,
      pageSize: pagination.pageSize,
      ...filters,
    })
    tableData.value = data.list || []
    pagination.total = data.total || 0
  } catch (err) {
    ElMessage.error(err.message || '加载列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filters.title = ''
  filters.status = ''
  pagination.page = 1
  loadData()
}

function openDialog(mode, row = null) {
  dialogMode.value = mode
  dialogVisible.value = true
  if (mode === 'update' && row) {
    currentId.value = row.id
    Object.assign(form, {
      title: row.title,
      type: row.type,
      status: row.status,
      content: row.content,
    })
  } else {
    currentId.value = null
    Object.assign(form, {
      title: '',
      type: 'notice',
      status: 'draft',
      content: '',
    })
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await noticeApi.create(form)
      ElMessage.success('公告发布成功')
    } else {
      await noticeApi.update(currentId.value, form)
      ElMessage.success('公告更新成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  try {
    await noticeApi.remove(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (err) {
    ElMessage.error(err.message || '删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.table-card {
  margin-top: 16px;
}
.pagination-box {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
</style>
```
