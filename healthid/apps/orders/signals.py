from django.dispatch import receiver
from django.db.models.signals import post_save
from healthid.apps.orders.models import Suppliers
from random import randint


@receiver(signal=post_save, sender=Suppliers)
def generate_supplier_id(
        sender,
        instance,
        update_fields=['supplier_id'],
        **kwargs):
    """
    method to automatically generate supplier ID based on
    supplier's name, id, and address line 1
    """
    supplier_name = instance.name[slice(3)].upper()
    random_number = randint(100, 999)
    instance.supplier_id = 'S-{}{}'.format(supplier_name, random_number)
    post_save.disconnect(generate_supplier_id, sender=Suppliers)
    instance.save()
    post_save.connect(generate_supplier_id, sender=Suppliers)
