from django.core.exceptions import ObjectDoesNotExist
from graphql import GraphQLError
from healthid.apps.authentication.models import User


class UserModelQuery:
    """
    this class create queries for the role
    """

    def query_user_id(self, id):
        try:
            user = User.objects.get(id=id)
            return user
        except ObjectDoesNotExist:
            raise GraphQLError(f"User with { id } id does not exist.")
