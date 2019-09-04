from django.db import models
from healthid.models import BaseModel
from healthid.apps.profiles.models import Profile
from healthid.apps.preference.models import Currency


class CustomerCredit(BaseModel):
    """
        Customer credit account model
    """
    customer = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, null=True, related_name="wallet")
    store_credit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    credit_currency = models.ForeignKey(
        Currency, on_delete=models.SET_NULL, null=True,
        related_name="currency")
