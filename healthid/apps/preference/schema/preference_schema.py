import json
from collections import namedtuple

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.preference.models import Currency, Preference, Timezone
from healthid.utils.auth_utils.decorator import master_admin_required


class TimezoneType(DjangoObjectType):
    class Meta:
        model = Timezone


class PreferenceType(DjangoObjectType):
    class Meta:
        model = Preference


def _json_object_hook(d):
    # Converting JSON to Python objects
    return namedtuple('X', d.keys())(*d.values())


def json_to_obj(data):
    return json.loads(data, object_hook=_json_object_hook)


class RawCurrency(graphene.ObjectType):
    # Structures the JSON output returned in GraphQL
    name = graphene.String()
    symbol = graphene.String()
    symbol_native = graphene.String()
    decimal_digits = graphene.Int()
    rounding = graphene.Int()
    code = graphene.String()
    name_plural = graphene.String()
    business_id = graphene.String()


class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency


class Query(graphene.ObjectType):
    """
    Return all time zones.
    Return a list of currencies or return a single curency specified.
    """
    timezones = graphene.List(TimezoneType)
    outlet_timezone = graphene.Field(PreferenceType,
                                     id=graphene.String())

    currencies = graphene.List(RawCurrency)
    currency = graphene.Field(
        CurrencyType,
        id=graphene.String(),
        name=graphene.String(),
        symbol=graphene.String(),
        symbol_native=graphene.String(),
        decimal_digits=graphene.Int(),
        rounding=graphene.Int(),
        code=graphene.String(),
        name_plural=graphene.String(),
        business_id=graphene.String()
    )
    success = graphene.List(graphene.String)

    @login_required
    @master_admin_required
    def resolve_timezones(self, info, **kwargs):
        return Timezone.objects.all()

    @login_required
    def resolve_outlet_timezone(self, info, **kwargs):
        id = kwargs.get('id')

        try:
            preference = Preference.objects.get(id=id)

            return preference
        except ObjectDoesNotExist:
            raise GraphQLError(
                'Preference with {} id does not exist'.format(id))

    @login_required
    def resolve_currencies(self, args):
        # returns all currencies from the fixture file
        currencies = Currency.get_currency_formats()
        return json_to_obj(json.dumps(currencies))

    @login_required
    def resolve_currency(self, info, **kwargs):
        # returns currency from db by currency name
        name = kwargs.get('name')

        if name is not None:
            return Currency.objects.get(name=name)
        return None
