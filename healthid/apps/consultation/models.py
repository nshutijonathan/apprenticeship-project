from django.db import models
from healthid.apps.outlets.models import Outlet


class ExpectedTimeDuration(models.Model):
    time = models.CharField(max_length=50, unique=True)


class ConsultantRole(models.Model):
    name = models.CharField(max_length=50, unique=True)


class ApprovedDeliveryFormat(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Consultation(models.Model):
    consultation_name = models.CharField(max_length=80)
    description = models.CharField(max_length=100)
    approved_delivery_formats = models.ForeignKey(
        ApprovedDeliveryFormat, on_delete=models.CASCADE)
    expected_time = models.ForeignKey(
        ExpectedTimeDuration, on_delete=models.CASCADE)
    consultant_role = models.ForeignKey(
        ConsultantRole, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    price_per_session = models.IntegerField()

    class Meta:
        unique_together = (("consultation_name", "approved_delivery_formats",
                            "expected_time"))
