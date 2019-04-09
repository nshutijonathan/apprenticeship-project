from django.db import models
from healthid.apps.business.models import Business
from healthid.apps.authentication.models import User


class Country(models.Model):
    name = models.CharField(max_length=244, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=244)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("name", "country"))

    def __str__(self):
        return self.name


class OutletKind(models.Model):
    name = models.CharField(max_length=244)

    def __str__(self):
        return self.name


class Outlet(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.ForeignKey(OutletKind, on_delete=models.CASCADE)
    name = models.CharField(max_length=244)
    address_line1 = models.CharField(max_length=244)
    address_line2 = models.CharField(max_length=244)
    lga = models.CharField(max_length=244)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=25)
    date_launched = models.DateField()
    prefix_id = models.CharField(max_length=9, null=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    user = models.ManyToManyField(User, related_name='users')

    class Meta:
        unique_together = (("name", "business"))

    def __str__(self):
        return self.name
