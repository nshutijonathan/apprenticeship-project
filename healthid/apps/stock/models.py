from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product, BatchInfo
from healthid.utils.app_utils.id_generator import id_gen


class StockCountTemplate(BaseModel):
    products = models.ManyToManyField(
        Product, related_name='products_to_count')
    schedule_time = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True)
    assigned_users = models.ManyToManyField(
        User, related_name='assigned_to')
    designated_users = models.ManyToManyField(
        User, related_name='designated_to')
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.id)


class StockCount(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    variance_reason = models.CharField(max_length=100)
    remarks = models.TextField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_template = models.ForeignKey(
        StockCountTemplate, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    stock_count_record = models.ManyToManyField(
        "StockCountRecord", related_name='stock_count_record')


class StockCountRecord(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    quantity_counted = models.PositiveIntegerField(blank=True, null=True)
    batch_info = models.ForeignKey(
        BatchInfo, on_delete=models.CASCADE, null=True, blank=True)


class StockTransferRecord(BaseModel):
    """Model to handle stock transfer records
    """
    batch = models.ForeignKey(
        BatchInfo, related_name='stock_transfer_records',
        on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()


class StockTransfer(BaseModel):
    """Model to handle stock transfer data
    """
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='stock_transfers', null=True)
    stock_transfer_record = models.ManyToManyField(
        StockTransferRecord, related_name='stock_transfer_record')
    sending_outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name='sending_outlet')
    destination_outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name='destination_outlet')
    created_at = models.DateField(auto_now_add=True)
    complete_status = models.BooleanField(default=False)
