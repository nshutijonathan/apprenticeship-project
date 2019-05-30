from django.db import models

from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen


class Order(BaseModel):
    '''Class to handle order data
    '''
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(
        max_length=9, default=id_gen, editable=False
    )
    name = models.TextField(null=False)
    product_autofill = models.BooleanField(default=True)
    supplier_autofill = models.BooleanField(default=True)
    destination_outlet = models.ManyToManyField(Outlet)
    delivery_date = models.DateField()
    sent_status = models.BooleanField(default=False)


class OrderDetails(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                 null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
