from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product, BatchInfo
from django.utils import timezone
from healthid.utils.app_utils.id_generator import id_gen


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


class StockCount(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    created_at = models.DateField(default=timezone.now, editable=False)
    updated_at = models.DateField(auto_now=True)
    variance_reason = models.CharField(max_length=100)
    remarks = models.TextField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_template = models.ForeignKey(
        StockCountTemplate, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    stock_count_record = models.ManyToManyField(
        "StockCountRecord", related_name='stock_count_record')


class StockCountRecord(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    quantity_counted = models.PositiveIntegerField(blank=True, null=True)
    batch_info = models.ForeignKey(
        BatchInfo, on_delete=models.CASCADE, null=True, blank=True)
