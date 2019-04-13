from django.db import models
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.outlets.models import Outlet

# Create your models here.


class Register(models.Model):
    name = models.CharField(max_length=244)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    receipt = models.ForeignKey(ReceiptTemplate, on_delete=models.CASCADE,
                                related_name='receipttemplate')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
