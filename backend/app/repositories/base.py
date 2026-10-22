from sqlalchemy import String, cast, func, or_, select


class Repository:
    model = None
    search_fields = ()

    async def get(self, db, id):
        return await db.get(self.model, id)

    def ordering(self):
        return [self.model.createdAt.desc(), self.model.id]

    async def list(self, db, page, page_size, keyword='', conditions=()):
        stmt = select(self.model).where(*conditions)
        if keyword:
            stmt = stmt.where(
                or_(
                    *[
                        cast(getattr(self.model, field), String).icontains(keyword, autoescape=True)
                        for field in self.search_fields
                    ]
                )
            )
        total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await db.scalars(
                stmt.order_by(*self.ordering()).offset((page - 1) * page_size).limit(page_size)
            )
        ).all()
        return rows, total

    async def create(self, db, data):
        row = self.model(**data)
        db.add(row)
        await db.flush()
        return row

    async def update(self, db, row, data):
        for key, value in data.items():
            setattr(row, key, value)
        await db.flush()
        return row

    async def delete(self, db, row):
        await db.delete(row)
        await db.flush()
