import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import City, Country, Outlet, OutletKind
from healthid.utils.app_utils.database import get_model_object


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


class OutletQuery(graphene.ObjectType):
    """
    Return a list of outlets.
    Or return a single outlet specified.
    """
    errors = graphene.Field(graphene.String)
    outlets = graphene.List(OutletType)
    outlet = graphene.Field(
        OutletType,
        id=graphene.Int(),
        name=graphene.String(),
        kind_id=graphene.Int(),
        phone_number=graphene.String(),
        address_line1=graphene.String(),
        address_line2=graphene.String(),
        lga=graphene.String(),
        city_id=graphene.Int(),
        date_launched=graphene.String(),
        prefix_id=graphene.String()
    )

    @login_required
    def resolve_outlets(self, info, **kwargs):
        return Outlet.objects.all()

    @login_required
    def resolve_outlet(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return get_model_object(Outlet, 'id', id)

        return None


class CityQuery(graphene.ObjectType):
    errors = graphene.Field(graphene.String)
    cities = graphene.List(CityType)
    city = graphene.Field(
        CityType,
        id=graphene.Int(),
        name=graphene.String(),
    )

    @login_required
    def resolve_cities(self, info, **kwargs):
        return City.objects.all()

    @login_required
    def resolve_city(self, info, **kwargs):
        city_id = kwargs.get('id')
        city_name = kwargs.get('name', ' ').title()
        if (city_id or city_name) is not None:
            city = City.objects.filter(
                Q(id=city_id) | Q(name=city_name)
            ).first()
            if city is None:
                raise GraphQLError('This city does not exist')
            return city
        raise GraphQLError('You must provide either a city Id or name')


class CountryQuery(graphene.ObjectType):
    errors = graphene.Field(graphene.String)
    countries = graphene.List(CountryType)
    country = graphene.Field(
        CountryType,
        id=graphene.Int(),
        name=graphene.String()
    )

    @login_required
    def resolve_countries(self, info, **kwargs):
        return Country.objects.all()

    @login_required
    def resolve_country(self, info, **kwargs):
        ctry_id = kwargs.get('id')
        ctry_name = kwargs.get('name', '').title()
        if (ctry_id or ctry_name) is not None:
            ctry = Country.objects.filter(
                Q(id=ctry_id) | Q(name=ctry_name)
            ).first()
            if ctry is None:
                raise GraphQLError('This country does not exist')
            return ctry
        raise GraphQLError('You must provide either a city id or name')


class Query(
    OutletQuery,
    CityQuery,
    CountryQuery,
    graphene.ObjectType
):
    pass
