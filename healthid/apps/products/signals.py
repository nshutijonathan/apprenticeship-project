import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.notifications_utils.handle_notifications import notify
from healthid.utils.messages.products_responses import \
    PRODUCTS_SUCCESS_RESPONSES


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


@receiver(post_save, sender=BatchInfo)
def set_nearest_expiry_date(sender, instance, **kwargs):
    """
    update the nearest_expiry_date when a batch is created/updated
    """
    product = instance.product
    if product.nearest_expiry_date is None or \
            product.nearest_expiry_date > instance.expiry_date:
        product.nearest_expiry_date = instance.expiry_date
        product.save()


@receiver(post_save, sender=Quantity)
def notify_quantity(sender, instance, created, **kwargs):
    """
    Method to generate notifications for proposed change in batch quantity.
    """
    if created:
        if not instance.quantity_remaining and instance.parent is None:
            instance.quantity_remaining = instance.quantity_received
            instance.save()
        if instance.parent_id:
            batch = instance.batch
            outlet_users = [user for user in batch.product.outlet.active_outlet_users if user.id != instance.proposed_by.id]  # noqa
            all_users = []
            for user in outlet_users:
                if str(user.role) == "Master Admin" or str(user.role) == \
                        "Operations Admin":
                    all_users.append(user)
            message = PRODUCTS_SUCCESS_RESPONSES[
                "batch_edit_proposal"].format(batch.batch_no)
            notify(all_users, message, event_name='batch_quantity')
    # if quantity instance is not a proposal,
    # we can check if the product quantity is low
    if not instance.parent_id:
        # set an arbitrary quantity threshold
        # we'll check for instances where product quantity
        # goes below this threshold
        quantity_threshold = 50
        product = instance.batch.product
        outlet_users = product.outlet.active_outlet_users

        # notify all outlet users.
        if product.quantity < quantity_threshold:
            message = PRODUCTS_SUCCESS_RESPONSES[
                "low_quantity_alert"].format(
                product.product_name,
                product.quantity)
            notify(outlet_users, message, event_name='product_quantity')


@receiver(post_save, sender=Quantity)
def track_sold_out_batches(sender, instance, **kwargs):
    """
    Function to track sold out batches
    """
    batch = instance.batch
    product = batch.product
    if instance.parent_id is None:
        if instance.quantity_remaining < 1:
            batch.sold_out = True
            batch.save()
            if product.nearest_expiry_date == batch.expiry_date:
                next_expiring_batch = product.batch_info.filter(
                    expiry_date__gt=batch.expiry_date, sold_out=False
                ).order_by('expiry_date').first()
                product.nearest_expiry_date = next_expiring_batch.expiry_date
                product.save()
