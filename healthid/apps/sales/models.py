from django.db import models

from healthid.models import BaseModel
from django.db.models import Sum
from django.db.models.signals import pre_save
from healthid.apps.products.models import Product
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.id_generator import id_gen
from healthid.apps.authentication.models import User


class PromotionType(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Promotion(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    title = models.CharField(max_length=140, unique=True)
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.CASCADE)
    description = models.TextField()
    products = models.ManyToManyField(Product, blank=True)
    discount = models.DecimalField(decimal_places=2, max_digits=10)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class SalesPrompt(BaseModel):
    prompt_title = models.CharField(max_length=244, unique=True)
    description = models.CharField(
        max_length=244, default="Sales prompt descripttion:")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.prompt_title


class Cart(models.Model):
    '''
    defines cart model.

    args:
        user: owner of the cart.
        items: products along with the quantity and their total that
               have been added to the cart
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem')

    @property
    def total(self):
        '''
        method that calculates the total price of all the items in cart
        '''
        return self.items.all().aggregate(Sum('item_total'))['item_total__sum']


class CartItem(models.Model):
    '''
    defines cart item model

    args:
        product: product to be added to cart
        quantity: amount of product to be added to cart
        item_total: price of the product based on the quantity
    '''
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    item_total = models.DecimalField(default=0.00,
                                     max_digits=10,
                                     decimal_places=2)

    def __str__(self):
        return str(self.id)


def update_item_total(**kwargs):
    '''
    function that calculates the price of product being added to cart
    based on the quantity being added, this is triggered before a cart
    item is saved
    '''
    cart_item = kwargs.get('instance')
    cart_item.item_total = \
        cart_item.product.pre_tax_retail_price * cart_item.quantity


pre_save.connect(update_item_total, sender=CartItem)
