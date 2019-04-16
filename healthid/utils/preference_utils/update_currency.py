from healthid.apps.preference.models import Vat
from graphql.error import GraphQLError


def update_vate(outlet_vat_rate, preference):
    if outlet_vat_rate <= 100 and outlet_vat_rate > 0:
        vat_id = preference.vat_rate.id
        vat = Vat.objects.get(pk=vat_id)
        vat.rate = outlet_vat_rate
        vat.save()
        return vat.rate
    else:
        raise GraphQLError(
            'Vat rate should not be more than 100 and it should be positive')
