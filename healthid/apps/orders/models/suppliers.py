from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.business.models import Business
from healthid.apps.outlets.models import City, Outlet, Country
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen
from healthid.apps.orders.enums.suppliers import PaymentTermsType


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
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    supplier_id = models.CharField(max_length=9, null=False)
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='supplier_creator')
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE,
        related_name='supplier_business', null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedEdit",
                               null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def get_supplier_contacts(self):
        """
        get contacts of a supplier

        Returns:
            list: contacts of a single supplier
        """
        return SuppliersContacts.objects.all().filter(
            supplier=(self.parent or self.id))

    @property
    def get_supplier_meta(self):
        """
        get meta data of a supplier

        Returns:
            list: meta data of a single supplier
        """
        return SuppliersMeta.objects.all().filter(
            supplier=(self.parent or self.id))


class SuppliersContacts(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100, null=True)
    mobile_number = models.CharField(max_length=100, null=True)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    lga = models.CharField(max_length=255, null=True)
    edit_request_id = models.CharField(max_length=255, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedEdit",
                               null=True, blank=True)


class SuppliersMeta(BaseModel):
    display_name = models.CharField(max_length=100, unique=True, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    logo = models.URLField(null=True)
    payment_terms = models.CharField(
        max_length=100, choices=PaymentTermsType.choices(), null=True)
    credit_days = models.IntegerField(null=True)
    commentary = models.TextField(null=True)
    admin_comment = models.TextField(null=True)
    edit_request_id = models.CharField(max_length=255, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedEdit",
                               null=True, blank=True)


class SupplierNote(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    outlet = models.ManyToManyField(Outlet, related_name='supplier_note')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='note_creator')
    note = models.TextField(default="user note about this supplier")


class SupplierRating(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    rating = models.IntegerField(null=False, default=0)
