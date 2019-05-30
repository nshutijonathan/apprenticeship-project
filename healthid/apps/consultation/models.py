from django.db import models

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.id_generator import ID_LENGTH, id_gen


class ExpectedTimeDuration(BaseModel):
    time = models.CharField(max_length=50, unique=True)


class ConsultantRole(BaseModel):
    name = models.CharField(max_length=50, unique=True)


class ApprovedDeliveryFormat(BaseModel):
    name = models.CharField(max_length=50, unique=True)


class Consultation(BaseModel):
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


class ScheduleConsultation(models.Model):
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    consultants = models.ManyToManyField(User)
    customer_name = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=100, default='Not Paid')
    consultation_type = models.ForeignKey(
        Consultation, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return (f'''{self.id}
        Customer Name: {self.customer_name}
        ''')
