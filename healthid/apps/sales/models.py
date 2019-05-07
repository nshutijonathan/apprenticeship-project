from django.db import models
from healthid.apps.products.models import Product
from healthid.apps.outlets.models import Outlet


class SalesPrompt(models.Model):
    prompt_title = models.CharField(max_length=244, unique=True)
    description = models.CharField(
        max_length=244, default="Sales prompt descripttion:")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.prompt_title
