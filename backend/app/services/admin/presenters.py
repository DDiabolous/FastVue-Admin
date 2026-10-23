from app.repositories.admin.roles import AdminRoleRepository


def fields(row, names):
    return {name: getattr(row, name) for name in names}


def user_data(user, role):
    return {
        **fields(
            user,
            [
                'id',
                'username',
                'realName',
                'email',
                'gender',
                'phone',
                'location',
                'bio',
                'avatar',
                'coverImage',
                'role',
                'status',
                'createdAt',
            ],
        ),
        'roleName': role.roleName if role else '未分配角色',
        'permissions': role.permissions if role and role.status == 1 else [],
    }


async def public_user(db, user):
    return user_data(user, await AdminRoleRepository().by_key(db, user.role))
