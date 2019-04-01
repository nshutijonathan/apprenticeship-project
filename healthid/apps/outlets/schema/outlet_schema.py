import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import City, Country, Outlet, OutletKind


class OutletType(DjangoObjectType):
    class Meta:
        model = Outlet


class CityType(DjangoObjectType):
    class Meta:
        model = City


class CountryType(DjangoObjectType):
    class Meta:
        model = Country


class OutletKindType(DjangoObjectType):
    class Meta:
        model = OutletKind


class Query(graphene.ObjectType):
    """
    Return a list of outlets.
    Or return a single outlet specified.
    """
    outlets = graphene.List(OutletType)
    outlet = graphene.Field(OutletType, id=graphene.Int(),
                            name=graphene.String(),
                            kind_id=graphene.Int(),
                            phone_number=graphene.String(),
                            address_line1=graphene.String(),
                            address_line2=graphene.String(),
                            lga=graphene.String(),
                            city_id=graphene.Int(),
                            date_launched=graphene.String(),
                            prefix_id=graphene.String())

    @login_required
    def resolve_outlets(self, info, **kwargs):
        return Outlet.objects.all()

    @login_required
    def resolve_outlet(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Outlet.objects.get(pk=id)

        return None
