from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import City, Outlet
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen


class Tier(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PaymentTerms(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Suppliers(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True, null=True)
    mobile_number = models.CharField(max_length=100)
    rating = models.IntegerField(null=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    lga = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    logo = models.URLField(null=True)
    commentary = models.TextField(null=True)
    payment_terms = models.ForeignKey(PaymentTerms, on_delete=models.CASCADE)
    credit_days = models.IntegerField(null=True)
    supplier_id = models.CharField(max_length=9, null=False)
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='supplier_creator')
    admin_comment = models.TextField(null=True)
    outlet = models.ManyToManyField(Outlet)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedEdit",
                               null=True, blank=True)

    def __str__(self):
        return self.name


class SupplierNote(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    outlet = models.ManyToManyField(Outlet, related_name='supplier_note')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='note_creator')
    note = models.TextField(default="user note about this supplier")
