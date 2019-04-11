import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.preference.models import Preference, Timezone
from healthid.utils.auth_utils.decorator import master_admin_required


class TimezoneType(DjangoObjectType):
    class Meta:
        model = Timezone


class PreferenceType(DjangoObjectType):
    class Meta:
        model = Preference


class Query(graphene.ObjectType):
    """
    Return all time zones.
    """
    timezones = graphene.List(TimezoneType)
    outlet_timezone = graphene.Field(PreferenceType,
                                     id=graphene.String())

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
