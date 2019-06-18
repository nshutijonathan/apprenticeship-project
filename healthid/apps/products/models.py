from decimal import Decimal

from django.db import models
from taggit.managers import TaggableManager

from healthid.apps.authentication.models import User
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.manager import BaseManager
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen


class ProductCategory(BaseModel):
    name = models.CharField(max_length=50, unique=True)


class MeasurementUnit(BaseModel):
    name = models.CharField(max_length=50, unique=True)


class ProductManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Product(BaseModel):
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=244, unique=True)
    measurement_unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.CASCADE)
    sku_number = models.CharField(max_length=100, null=False)
    is_approved = models.BooleanField(default=False)
    description = models.CharField(max_length=150)
    brand = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=50)
    vat_status = models.CharField(max_length=50)
    sales_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    nearest_expiry_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True)
    preferred_supplier = models.ForeignKey(
        Suppliers, related_name='prefered', on_delete=models.CASCADE)
    backup_supplier = models.ForeignKey(
        Suppliers, related_name='backup', on_delete=models.CASCADE)
    outlet = models.ManyToManyField(Outlet)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,
        related_name='product_creator')
    admin_comment = models.TextField(null=True)
    tags = TaggableManager()
    markup = models.IntegerField(default=25)
    pre_tax_retail_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=False)
    auto_price = models.BooleanField(default=False)
    loyalty_weight = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="proposedEdit",
        null=True,
        blank=True)
    image = models.URLField(
        default='https://res.cloudinary.com/dojaopytm/image/upload/'
        'v1558444184/productPlaceholder.png')
    is_active = models.BooleanField(default=True)
    reorder_point = models.IntegerField(default=0)
    reorder_max = models.IntegerField(default=0)

    '''all_products model manager returns both all products including
    deactivated products i.e Products.all_products.all() returns both
    active and deactivated products use it when you need deactivate
    products as well.'''
    all_products = models.Manager()

    '''objects model manager returns only activated products i.e
    Products.objects.all() returns only active products use it when
    you don't need deactivated products.'''
    objects = ProductManager()

    @property
    def get_tags(self):
        return self.tags.all()

    def __str__(self):
        return self.product_name

    def __repr__(self):
        return (f'''<{self.product_name}>
        <Price: {self.sales_price}>
        ''')

    @property
    def quantity(self):
        """
        Get the total quantity of a given product.
        """
        product_quantities = self.product_quantities.filter(
            parent_id__isnull=True).aggregate(models.Sum('quantity_received'))
        return product_quantities['quantity_received__sum']

    @property
    def autofill_quantity(self):
        return self.reorder_max - self.quantity


class BatchInfo(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    batch_no = models.CharField(
        max_length=100, null=True, blank=True, editable=False)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    date_received = models.DateField(auto_now=False, null=True, blank=True)
    pack_size = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(auto_now=False, null=True, blank=True)
    unit_cost = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))
    commentary = models.TextField(blank=True, null=True)
    product = models.ManyToManyField(Product, related_name='batch_info')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_batches')
    outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name='outlet_batches')

    def __str__(self):
        return self.batch_no

    def __unicode__(self):
        return self.batch_no

    @property
    def quantity(self):
        """
        Property to return the total quantities of products
        in a batch.
        """
        batch_quantities = self.batch_quantities.filter(
            parent_id__isnull=True).aggregate(models.Sum('quantity_received'))
        return batch_quantities['quantity_received__sum']


class Quantity(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    product = models.ForeignKey(
        Product, related_name='product_quantities', on_delete=models.CASCADE)
    batch = models.ForeignKey(
        BatchInfo, on_delete=models.CASCADE, related_name='batch_quantities')
    quantity_received = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    proposed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='proposing_user',
        null=True, blank=True)
    authorized_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='approving_user',
        null=True, blank=True)
    comment = models.TextField(null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedQuantityChange",
                               null=True, blank=True)


class Survey(BaseModel):
    """
    Model class for survey used to conduct supplier
    price checks for products.
    """
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=50, unique=True)
    outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name='outlet_price_surveys')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_price_surveys')
    survey_closed = models.BooleanField(default=False)


class PriceCheckSurvey(BaseModel):
    """
    Model class for price check surveys.
    """
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_price_checks')
    supplier = models.ForeignKey(
        Suppliers, on_delete=models.CASCADE, related_name='supplier_prices')
    price = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))
    survey = models.ManyToManyField(Survey, related_name='survey_price_checks')
