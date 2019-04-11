import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role, User
from healthid.utils.auth_utils.decorator import master_admin_required


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude_fields = ['password']


class RoleType(DjangoObjectType):
    class Meta:
        model = Role


class Query(graphene.AbstractType):
    """
    Query to authenticate a user.
    """
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    role = graphene.Field(
        RoleType,
        id=graphene.String(),
        name=graphene.String())
    roles = graphene.List(RoleType)

    def resolve_users(self, info):
        """
        Resolver method for users field.
        """
        return User.objects.all()

    def resolve_me(self, info):
        """
        Resolver method to check if a user is authenticated.
        """
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Please login to continue.")
        return user

    @staticmethod
    @login_required
    @master_admin_required
    def resolve_role(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            return Role.objects.get(pk=id)

        if name is not None:
            return Role.objects.get(name=name)
        return None

    @staticmethod
    @login_required
    @master_admin_required
    def resolve_roles(self, info, **Kwargs):
        return Role.objects.all()


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    """
    Class to override default JSONWebTokenMutation to
    return the user object along with the authentication token.
    """
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)
