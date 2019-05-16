from django.db import models
from healthid.apps.products.models import Product
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.id_generator import id_gen


class PromotionType(models.Model):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Promotion(models.Model):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    title = models.CharField(max_length=140, unique=True)
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.CASCADE)
    description = models.TextField()
    products = models.ManyToManyField(Product, blank=True)
    discount = models.DecimalField(decimal_places=2, max_digits=10)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class SalesPrompt(models.Model):
    prompt_title = models.CharField(max_length=244, unique=True)
    description = models.CharField(
        max_length=244, default="Sales prompt descripttion:")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.prompt_title
