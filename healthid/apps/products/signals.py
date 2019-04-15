from django.dispatch import receiver
from django.db.models.signals import post_save
from healthid.apps.products.models import Product


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
