import graphene
from graphene_django import DjangoObjectType

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import Outlet


class ActiveOutletType(DjangoObjectType):
    class Meta:
        model = Outlet


class UserType(DjangoObjectType):
    active_outlet = graphene.Field(ActiveOutletType)

    class Meta:
        model = User
        exclude_fields = ['password']

    def resolve_active_outlet(self, info, **kwargs):
        """
        get's outlet a user is active in

        Returns:
            obj: outlet user is active in
        """
        return self.active_outlet
