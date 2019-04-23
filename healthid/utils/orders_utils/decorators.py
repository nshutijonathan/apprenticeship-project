from functools import wraps

from graphql.execution.base import ResolveInfo
from graphql_jwt.exceptions import PermissionDenied


def verify_user(test_function, exc=PermissionDenied()):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            info = [arg for arg in args if isinstance(arg, ResolveInfo)]
            user = info[0].context.user
            if test_function(user):
                return func(*args, **kwargs)
            raise exc
        return wrapper
    return decorator


operations_or_master_admin_required = verify_user(
    lambda u: str(u.role) == 'Master Admin'
    or
    str(u.role) == 'Operations Admin')
