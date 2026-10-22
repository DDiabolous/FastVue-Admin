from app.repositories.audit import AuditRepository

from .presenters import fields


def audit(db, context, action, target, category='operation', status='success'):
    AuditRepository().append(
        db,
        {
            'operator': context.operator[:100],
            'action': action,
            'target': str(target)[:200],
            'category': category,
            'status': status,
            'ip': context.ip[:64],
        },
    )


class AuditService:
    async def list(self, db, page, page_size, keyword, category):
        rows, total = await AuditRepository().list_category(db, page, page_size, keyword, category)
        names = ['id', 'time', 'operator', 'action', 'target', 'category', 'status', 'ip']
        return {'list': [fields(row, names) for row in rows], 'total': total}
