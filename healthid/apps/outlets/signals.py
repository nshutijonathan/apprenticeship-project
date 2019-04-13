from django.dispatch import receiver
from django.db.models.signals import post_save
from healthid.apps.outlets.models import Outlet
from healthid.apps.preference.models import Preference, Timezone, Currency


@receiver(post_save, sender=Outlet)
def set_prefix(sender, update_fields=['prefix_id'], *args, **kwargs):
    """
    Method to generate prefix id and default timezone using signals
    Generate default currency using signals
    """
    outlet = kwargs['instance']
    default_timezone = Timezone.objects.get(pk="285461788")
    default_currency = Currency.objects.get_or_create(
        pk="4jatbw5sm",
        name="Nigerian Naira",
        symbol="₦",
        symbol_native="₦",
        decimal_digits=2,
        rounding=0,
        code="NGN",
        name_plural="Nigerian nairas"
    )
    preference = Preference()
    preference.outlet = outlet
    # get the set defualt currency
    preference.outlet_currency = default_currency[0]
    preference.outlet_timezone = default_timezone
    preference.save()
    outlet.preference_id = preference.id
    outlet_name = outlet.name[slice(3)].upper()
    business_name = outlet.business.trading_name[slice(2)].upper()
    outlet_id = (str(outlet.id)).zfill(3)
    outlet.prefix_id = '{}{}-{}'.format(business_name, outlet_id, outlet_name)
    post_save.disconnect(set_prefix, sender=Outlet)
    outlet.save()
    post_save.connect(set_prefix, sender=Outlet)
