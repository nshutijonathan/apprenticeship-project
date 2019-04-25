from decimal import Decimal

from django.db import models
from taggit.managers import TaggableManager

from healthid.apps.orders.models import Suppliers
from healthid.utils.app_utils.id_generator import id_gen


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)


class MeasurementUnit(models.Model):
    name = models.CharField(max_length=50)


class Product(models.Model):
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=244, unique=True)
    measurement_unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.CASCADE)
    pack_size = models.CharField(max_length=50)
    sku_number = models.CharField(max_length=100, null=False)
    is_approved = models.BooleanField(default=False)
    description = models.CharField(max_length=150)
    brand = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=50)
    vat_status = models.CharField(max_length=50)
    quality = models.CharField(max_length=50)
    sales_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    created_date = models.DateField(auto_now=True, auto_now_add=False)
    nearest_expiry_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True)
    prefered_supplier = models.ForeignKey(
        Suppliers, related_name='prefered', on_delete=models.CASCADE)
    backup_supplier = models.ForeignKey(
        Suppliers, related_name='backup', on_delete=models.CASCADE)
    tags = TaggableManager()
    markup = models.IntegerField(default=25)
    pre_tax_retail_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True
    )
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=False)
    auto_price = models.BooleanField(default=False)
    loyalty_weight = models.IntegerField(default=0)

    @property
    def get_tags(self):
        return self.tags.all()

    def __str__(self):
        return (f'''<{self.product_name}>
        <Price: {self.sales_price}>
        ''')


class BatchInfo(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    batch_no = models.CharField(
        max_length=100, null=True, blank=True, editable=False
    )
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    date_received = models.DateField(auto_now=False, null=True, blank=True)
    pack_size = models.CharField(max_length=100, null=True, blank=True)
    quantity_received = models.PositiveIntegerField(blank=True, null=True)
    expiry_date = models.DateField(auto_now=False, null=True, blank=True)
    unit_cost = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00')
    )
    commentary = models.TextField(blank=True, null=True)
    product = models.ManyToManyField(Product, related_name='batch_info')

    def __str__(self):
        return self.batch_no

    def __unicode__(self):
        return self.batch_no
