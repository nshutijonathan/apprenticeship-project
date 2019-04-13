from django.db import models
from healthid.utils.preference_utils.currency_fixture import MONEY_FORMATS
from healthid.utils.app_utils.id_generator import id_gen


class Timezone(models.Model):

    name = models.CharField(max_length=244, unique=True)
    time_zone = models.CharField(
        max_length=244, unique=True)

    def __str__(self):
        return self.time_zone


class Currency(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=244, unique=True)
    symbol = models.CharField(max_length=244)
    symbol_native = models.CharField(max_length=244)
    decimal_digits = models.IntegerField()
    rounding = models.IntegerField()
    code = models.CharField(max_length=244, unique=True)
    name_plural = models.CharField(max_length=244)

    def __str__(self):
        return self.name

    money_formats = MONEY_FORMATS

    @classmethod
    def get_currency_formats(cls):
        """
        :rtype: list of all currency
        """
        return cls.money_formats


class Preference(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    outlet_timezone = models.ForeignKey(
        Timezone, on_delete=models.CASCADE)
    outlet_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
