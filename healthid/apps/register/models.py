from django.db import models

from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.apps.receipts.models import ReceiptTemplate


class Register(BaseModel):
    name = models.CharField(max_length=244)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE,
                               related_name='outlet_register')
    receipt = models.ForeignKey(ReceiptTemplate, on_delete=models.CASCADE,
                                related_name='receipttemplate')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
