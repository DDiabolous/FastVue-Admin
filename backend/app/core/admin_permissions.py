PERMISSIONS = {
    f'system:{resource}:{action}'
    for resource, actions in {
        'users': ['read', 'create', 'update', 'delete'],
        'roles': ['read', 'create', 'update', 'delete'],
        'dictionary': ['read', 'create', 'update', 'delete'],
        'settings': ['read', 'update'],
        'logs': ['read'],
        'menus': ['read'],
    }.items()
    for action in actions
}


def can(permissions, permission):
    return '*' in permissions or permission in permissions


def covers(permissions, target):
    return '*' in permissions or ('*' not in target and set(target) <= set(permissions))
