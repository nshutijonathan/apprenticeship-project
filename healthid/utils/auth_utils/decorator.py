from graphql import GraphQLError
from healthid.apps.business.models import Business
from graphql_jwt.decorators import user_passes_test


def master_admin_required(func):
    def wrapper(*args, **kwargs):
        user = args[1].context.user
        if str(user.role) == "Master Admin":
            return func(*args, **kwargs)
        raise GraphQLError("Permission denied")

    return wrapper


def check_user_business(user):
    try:
        Business.objects.get(user=user)
    except Business.DoesNotExist:
        raise GraphQLError("Sorry, You must be attached to a business!")


def admin_required(func):
    def wrapper(*args, **kwargs):
        user = args[1].context.user
        allowed_role = ('Master Admin', 'Manager')
        check_user_business(user)
        if str(user.role) in allowed_role:
            return func(*args, **kwargs)
        raise GraphQLError("Permission denied")

    return wrapper


operations_or_master_admin_required = user_passes_test(lambda u: str(
    u.role).__contains__('Master Admin') or str(u.role).__contains__(
        'Operations Admin'))
