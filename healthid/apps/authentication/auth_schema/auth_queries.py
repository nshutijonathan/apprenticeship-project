from healthid.apps.authentication.models import User, Role
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.authentication.utils.decorator import master_admin_required
import graphene


class RoleType(DjangoObjectType):
    class Meta:
        model = Role


class Query(graphene.ObjectType):
    """
       Query to authenticate a user.
       """

    role = graphene.Field(RoleType, id=graphene.String(), name=graphene.String())
    roles = graphene.List(RoleType)

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
