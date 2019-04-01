from django.dispatch import receiver
from django.db.models.signals import post_save
from healthid.apps.outlets.models import Outlet


@receiver(post_save, sender=Outlet)
def set_prefix(sender, update_fields=['prefix_id'], *args, **kwargs):
    """
    Method to generate prefix id using signals
    """
    outlet = kwargs['instance']
    outlet_name = outlet.name[slice(3)].upper()
    business_name = outlet.business.trading_name[slice(2)].upper()
    outlet_id = (str(outlet.id)).zfill(3)
    outlet.prefix_id = '{}{}-{}'.format(business_name, outlet_id, outlet_name)
    post_save.disconnect(set_prefix, sender=Outlet)
    outlet.save()
    post_save.connect(set_prefix, sender=Outlet)
