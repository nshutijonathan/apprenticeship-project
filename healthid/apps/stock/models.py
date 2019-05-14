from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product


class StockCountTemplate(models.Model):
    products = models.ManyToManyField(
        Product, related_name='products_to_count')
    schedule_time = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True)
    assigned_users = models.ManyToManyField(
        User, related_name='assigned_to')
    designated_users = models.ManyToManyField(
        User, related_name='designated_to')
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
