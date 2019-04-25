from graphql import GraphQLError
from graphql_jwt.decorators import user_passes_test

from healthid.apps.business.models import Business


def master_admin_required(func):
    def wrapper(*args, **kwargs):
        user = args[1].context.user
        if str(user.role) == "Master Admin":
            return func(*args, **kwargs)
        raise GraphQLError("Permission denied")

    return wrapper


def check_user_in_business(user):
    user_business = Business.objects.filter(user=user)
    if user_business.count() < 1:
        raise GraphQLError('Sorry, You are not attached to a Business!.')


def admin_required(func):
    def wrapper(*args, **kwargs):
        user = args[1].context.user
        allowed_role = ('Master Admin', 'Manager')
        check_user_in_business(user)
        if str(user.role) in allowed_role:
            return func(*args, **kwargs)
        raise GraphQLError("Permission denied")

    return wrapper


operations_or_master_admin_required = user_passes_test(lambda u: str(
    u.role).__contains__('Master Admin') or str(u.role).__contains__(
        'Operations Admin'))
admin_or_manager_required = user_passes_test(
    lambda u: str(u.role).__contains__('Admin') or str(
        u.role).__contains__('Manager'))
