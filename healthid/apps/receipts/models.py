from django.db import models

from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.id_generator import ID_LENGTH, id_gen


class ReceiptTemplate(models.Model):
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    cashier = models.BooleanField(default=True)
    discount_total = models.BooleanField(default=True)
    receipt_no = models.BooleanField(default=True)
    receipt = models.BooleanField(default=True)
    subtotal = models.BooleanField(default=True)
    total_tax = models.BooleanField(default=True)
    amount_to_pay = models.BooleanField(default=True)
    purchase_total = models.BooleanField(default=True)
    change_due = models.BooleanField(default=True)
    loyalty = models.BooleanField(default=True)
    loyalty_earned = models.BooleanField(default=True)
    loyalty_balance = models.BooleanField(default=True)
    barcode = models.BooleanField(default=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class FieldSet(models.Model):
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    cashier = models.CharField(max_length=244, default="Served by:")
    change_due = models.CharField(max_length=244, default="Change due:")
    receipt_no = models.CharField(max_length=244, default="Receipt no:")
    receipt = models.CharField(max_length=244, default="Receipt:")
    discount_total = models.CharField(max_length=244, default="Subtotal:")
    subtotal = models.CharField(max_length=244, default="Subtotal:")
    total_tax = models.CharField(max_length=244, default="Tax:")
    amount_to_pay = models.CharField(max_length=244, default="Amount to pay:")
    purchase_total = models.CharField(max_length=244, default="Purchase total")
    loyalty = models.CharField(max_length=244, default="Loyalty:")
    loyalty_earned = models.CharField(
        max_length=244, default="Loyalty earned on purchase:")
    loyalty_balance = models.CharField(
        max_length=244, default="Current Loyalty Balance:")
    footer = models.CharField(
        max_length=244, default="Thank you for shopping with us.")
    receipt_template = models.ForeignKey(
        ReceiptTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return self.id
