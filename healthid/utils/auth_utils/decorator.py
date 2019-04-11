from graphql import GraphQLError


def master_admin_required(func):
    def wrapper(*args, **kwargs):
        user = args[1].context.user
        if str(user.role) == "Master Admin":
            return func(*args, **kwargs)
        raise GraphQLError("Permission denied")

    return wrapper
