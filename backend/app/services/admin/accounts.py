from asyncio import to_thread

from app.core.errors import AppError
from app.core.admin_permissions import covers
from app.core.passwords import hash_password
from app.repositories.admin.auth import AdminSessionRepository
from app.repositories.admin.roles import AdminRoleRepository
from app.repositories.admin.accounts import AdminAccountRepository

from app.services.admin.base import ResourceService, non_null
from app.services.admin.presenters import user_data


class AdminAccountService(ResourceService):
    repository = AdminAccountRepository()
    resource = 'users'

    async def present_list(self, db, rows):
        roles = {
            role.roleKey: role
            for role in await AdminRoleRepository().by_keys(db, {row.role for row in rows})
        }
        return [user_data(row, roles.get(row.role)) for row in rows]

    async def manageable(self, db, principal, row):
        if row.builtin:
            raise AppError(400, '内置管理员请在个人中心维护资料，不可修改或删除')
        role = await AdminRoleRepository().by_key(db, row.role)
        if not role or not covers(principal.permissions, role.permissions):
            raise AppError(403, '不能维护超出自身权限的账号')

    async def prepare(self, db, principal, data, row):
        data = dict(data)
        password = data.pop('password', None)
        non_null(data)
        if row:
            await self.manageable(db, principal, row)
        role = await AdminRoleRepository().by_key(db, data.get('role', row.role if row else ''))
        if not role or role.status != 1 or not covers(principal.permissions, role.permissions):
            raise AppError(403, '不能分配超出自身权限或已停用的角色')
        if password:
            data['password_hash'] = await to_thread(hash_password, password)
        if row and (
            password or data.get('status') == 0 or ('role' in data and data['role'] != row.role)
        ):
            await AdminSessionRepository().revoke_user(db, row.id)
        return data

    async def check_delete(self, db, principal, row):
        await self.manageable(db, principal, row)
        if row.id == principal.user.id:
            raise AppError(400, '不能删除当前账号')
