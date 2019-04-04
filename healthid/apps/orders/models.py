from django.db import models

from healthid.apps.outlets.models import City


class Tier(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PaymentTerms(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Suppliers(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
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

    def __str__(self):
        return self.name
