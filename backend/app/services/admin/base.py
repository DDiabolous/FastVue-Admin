from app.core.errors import AppError

from app.services.admin.audit import audit
from app.services.admin.presenters import fields


def non_null(data):
    if any(value is None for value in data.values()):
        raise AppError(422, '字段不能为 null')
    return data


class ResourceService:
    repository = None
    resource = ''
    public_fields = ()

    async def present_list(self, db, rows):
        return [fields(row, self.public_fields) for row in rows]

    async def list(self, db, page, page_size, keyword):
        rows, total = await self.repository.list(db, page, page_size, keyword)
        return {'list': await self.present_list(db, rows), 'total': total}

    async def prepare(self, db, principal, data, row):
        return non_null(dict(data))

    async def check_delete(self, db, principal, row):
        pass

    async def get_required(self, db, id):
        row = await self.repository.get(db, id)
        if not row:
            raise AppError(404, '记录不存在')
        return row

    async def create(self, db, principal, context, data):
        data = await self.prepare(db, principal, data, None)
        row = await self.repository.create(db, data)
        audit(db, context, f'新增{self.resource}', row.id)
        await db.commit()

    async def update(self, db, principal, context, id, data):
        row = await self.get_required(db, id)
        data = await self.prepare(db, principal, data, row)
        await self.repository.update(db, row, data)
        audit(db, context, f'编辑{self.resource}', row.id)
        await db.commit()

    async def delete(self, db, principal, context, id):
        row = await self.get_required(db, id)
        await self.check_delete(db, principal, row)
        await self.repository.delete(db, row)
        audit(db, context, f'删除{self.resource}', id)
        await db.commit()
