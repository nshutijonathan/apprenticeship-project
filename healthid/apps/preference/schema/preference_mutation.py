import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.preference.models import Currency, Preference, Timezone
from healthid.apps.preference.schema.preference_schema import (CurrencyType,
                                                               TimezoneType)
from healthid.utils.auth_utils.decorator import master_admin_required


def get_timezone(outlet_timezone_id):
    try:
        outlet_timezone = Timezone.objects.get(pk=outlet_timezone_id)
        return outlet_timezone

    except ObjectDoesNotExist:
        raise GraphQLError(
            'Timezone with id {} does not exist'.format(outlet_timezone_id))


def get_currency_from_file(name):
    # filters currency by name from the ist of currencies
    currencies = Currency.get_currency_formats()

    currency = Currency()
    default_currency = list(
        filter(lambda money: money['name'] == name, currencies))
    if default_currency:
        for(key, value) in default_currency[0].items():
            if key is not None:
                setattr(currency, key, value)
        return currency
    raise GraphQLError(
        'Currency with name {} does not exist'.format(name))


def get_currency(currency_name, **kwargs):
    # checks for currency in models before updating it.
    currencies = Currency.objects.filter(name=currency_name)
    if not currencies.exists():
        currency = get_currency_from_file(currency_name)
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(currency, key, value)
        currency.save()
        return currency
    return currencies.first()


class UpdatePreference(graphene.Mutation):
    """
    Updates a timezone
    """
    outlet_currency = graphene.Field(CurrencyType)
    outlet_timezone = graphene.Field(TimezoneType)
    success = graphene.String()

    class Arguments:
        outlet_timezone = graphene.String()
        preference_id = graphene.String(required=True)
        outlet_currency = graphene.String()

    @login_required
    @master_admin_required
    def mutate(self, info, **kwargs):
        try:
            outlet_timezone_id = kwargs.get('outlet_timezone')
            outlet_currency = kwargs.get('outlet_currency')
            preference_id = kwargs.get('preference_id')
            preference = Preference.objects.get(pk=preference_id)
            if outlet_timezone_id:
                outlet_timezone = get_timezone(outlet_timezone_id)
                preference.outlet_timezone = outlet_timezone
            if outlet_currency:
                currency = get_currency(outlet_currency, **kwargs)
                preference.outlet_currency_id = currency.id
            preference.save()

        except ObjectDoesNotExist:
            raise GraphQLError('Preference with this id does not exist')

        return UpdatePreference(
            outlet_timezone=preference.outlet_timezone,
            outlet_currency=preference.outlet_currency,
            success=("Preference updated successfully")
        )


class Mutation(graphene.ObjectType):
    update_preference = UpdatePreference.Field()
