import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from healthid.apps.products.models import BatchInfo, Product
from healthid.utils.app_utils.id_generator import id_gen


@receiver(post_save, sender=Product)
def generate_SKUNumber(sender, update_fields=['sku_number'], *args, **kwargs):
    """
    Method  generates skunumber using signals
    """
    product = kwargs['instance']
    product_id = (str(product.id)).zfill(6)
    product.sku_number = '{}'.format(product_id)
    post_save.disconnect(generate_SKUNumber, sender=Product)
    product.save()
    post_save.connect(generate_SKUNumber, sender=Product)


@receiver(post_save, sender=BatchInfo)
def generate_batch_no(sender, instance, created, **kwargs):
    if created:
        now = datetime.datetime.now()
        batch_no = "BN" + now.strftime("%Y%m%d%H%M") + "-" + id_gen()
        batch_info = instance
        batch_info.batch_no = batch_no
        post_save.disconnect(generate_batch_no, sender=BatchInfo)
        batch_info.save()
        post_save.connect(generate_batch_no, sender=BatchInfo)
