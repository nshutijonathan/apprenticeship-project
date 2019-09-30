from django.db import models
from django.db.models import Q

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product, BatchInfo
from healthid.utils.app_utils.id_generator import id_gen


APPROVAL_WAITING = "Waiting for approval"
COMPLETE = "Complete"
IN_PROGRESS = "In progress"
SCHEDULED_IN_ADVANCE = "Scheduled in advance"


class StockCountTemplate(BaseModel):
    products = models.ManyToManyField(
        Product, related_name='products_to_count')
    batches = models.ManyToManyField(
        BatchInfo, related_name='batches_to_count', blank=True)
    schedule_time = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50, default=SCHEDULED_IN_ADVANCE)
    is_closed = models.BooleanField(default=False)
    assigned_users = models.ManyToManyField(
        User, related_name='assigned_to')
    designated_users = models.ManyToManyField(
        User, related_name='designated_to')
    outlet = models.ForeignKey(Outlet, on_delete=models.DO_NOTHING, null=True)
    interval = models.PositiveIntegerField(null=True, blank=True)
    end_on = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='created_by', null=True, blank=True)
    scheduled = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['created_at', 'interval',
                        'end_on', 'created_by'],
                condition=Q(unique=True),
                name='unique_template_user'),

        ]

    def __str__(self):
        return str(self.id)

    def get_products(self):
        """
        Return a list of affiliated products
        """
        return [product.id for product in self.products.all()]

    def get_assigned_users(self):
        """
        Returns a list of affiliated assignees
        """
        return [user.id for user in self.assigned_users.all()]

    def get_designated_users(self):
        """
        Returns a list of affiliated admins
        """
        return [user.id for user in self.designated_users.all()]


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

    @property
    def update_template_status(self):
        """
        This method update the status of the stock count template
        """
        if not self.is_completed:
            self.stock_template.status = IN_PROGRESS

        if self.is_completed:
            self.stock_template.status = APPROVAL_WAITING

        if self.is_approved:
            self.stock_template.status = COMPLETE
            self.stock_template.is_closed = True
        self.stock_template.save()


class StockCountRecord(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    quantity_counted = models.PositiveIntegerField(blank=True, null=True)
    batch_info = models.ForeignKey(
        BatchInfo, on_delete=models.CASCADE, null=True, blank=True)


class StockTransferRecord(BaseModel):
    """
     Model to handle stock transfer records
    """
    batch = models.ForeignKey(
        BatchInfo, related_name='stock_transfer_records',
        on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()


class StockTransfer(BaseModel):
    """
    Model to handle stock transfer data
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
