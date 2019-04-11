import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.preference.models import Preference, Timezone
from healthid.apps.preference.schema.preference_schema import TimezoneType
from healthid.utils.auth_utils.decorator import master_admin_required


class UpdatePreference(graphene.Mutation):
    """
    Updates a timezone
    """
    outlet_timezone = graphene.Field(TimezoneType)
    success = graphene.String()

    class Arguments:
        outlet_timezone = graphene.String()
        preference_id = graphene.String(required=True)

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            outlet_timezone_id = kwargs.get('outlet_timezone')
            preference_id = kwargs.get('preference_id')
            outlet_timezone = Timezone.objects.get(pk=outlet_timezone_id)
            preference = Preference.objects.get(pk=preference_id)

            preference.outlet_timezone = outlet_timezone
            preference.save()
        except ObjectDoesNotExist:
            raise GraphQLError('Preference with this id does not exist')

        return UpdatePreference(
            outlet_timezone=outlet_timezone,
            success="Timezone has been updated to {}".format(
                outlet_timezone.name)
        )


class Mutation(graphene.ObjectType):
    update_preference = UpdatePreference.Field()
