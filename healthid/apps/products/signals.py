import datetime
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.notifications_utils.handle_notifications import notify


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


@receiver(post_save, sender=Product)
def set_retail_price(sender, update_fields=['sales_price '], *args, **kwargs):
    """Method to calculate retail price every time a product
    is saved to the database
    """
    product = kwargs['instance']
    """
    check if the product is being updated and automatic
    pricing is enabled
    """
    if not product._state.adding and product.auto_price:
        unit_cost = product.unit_cost
        markup = product.markup
        retail_price = unit_cost * Decimal(1 + markup / 100)
        product.sales_price = retail_price
        post_save.disconnect(set_retail_price, sender=Product)
        product.auto_price = False
        product.save()
        post_save.connect(set_retail_price, sender=Product)


@receiver(post_save, sender=Quantity)
def notify_quantity(sender, instance, created, **kwargs):
    """
    Method to generate notifications for proposed change in batch quantity.
    """
    if created:
        if instance.parent_id:
            batch = instance.batch
            outlet_users = batch.outlet.user.exclude(
                id=instance.proposed_by.id)
            all_users = []
            for user in outlet_users:
                if str(user.role) == "Master Admin" or str(user.role) == \
                        "Operations Admin":
                    all_users.append(user)
            message = ("Batch no: {} has a"
                       " proposed quantity edit.").format(batch.batch_no)
            notify(all_users, message, event_name='batch_quantity')
    # if quantity instance is not a proposal,
    # we can check if the product quantity is low
    if not instance.parent_id:
        # set an arbitrary quantity threshold
        # we'll check for instances where product quantity
        # goes below this threshold
        quantity_threshold = 50
        batch = instance.batch
        product = instance.product
        outlet_users = batch.outlet.user.all()

        # notify all outlet users.
        if product.quantity < quantity_threshold:
            message = "Low quantity alert!"
            message += " Product name: {}, Unit(s) left: {}." \
                .format(product.product_name,
                        product.quantity)
            notify(outlet_users, message, event_name='product_quantity')
