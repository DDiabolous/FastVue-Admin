from app.core.errors import AppError
from app.core.security import PERMISSIONS, covers
from app.repositories.auth import SessionRepository
from app.repositories.roles import RoleRepository
from app.repositories.users import UserRepository

from .base import ResourceService, non_null


class RoleService(ResourceService):
    repository = RoleRepository()
    resource = 'roles'
    public_fields = [
        'id',
        'roleKey',
        'roleName',
        'description',
        'permissions',
        'status',
        'createdAt',
    ]

    def manageable(self, principal, row):
        if row.builtin:
            raise AppError(400, '内置管理员角色不可修改或删除')
        if not covers(principal.permissions, row.permissions):
            raise AppError(403, '不能维护超出自身权限的角色')

    async def prepare(self, db, principal, data, row):
        data = non_null(dict(data))
        if row:
            self.manageable(principal, row)
        grants = data.get('permissions', row.permissions if row else [])
        if any(value not in PERMISSIONS and value != '*' for value in grants):
            raise AppError(422, '权限码无效')
        if not covers(principal.permissions, grants):
            raise AppError(403, '不能授予超出自身权限的权限')
        if row:
            if data.get(
                'roleKey', row.roleKey
            ) != row.roleKey and await UserRepository().role_is_bound(db, row.roleKey):
                raise AppError(400, '角色已被用户使用，请先调整用户角色')
            if data.get('status') == 0:
                await SessionRepository().revoke_role(db, row.roleKey)
        return data

    async def check_delete(self, db, principal, row):
        self.manageable(principal, row)
        if await UserRepository().role_is_bound(db, row.roleKey):
            raise AppError(400, '角色已被用户使用，请先调整用户角色')
