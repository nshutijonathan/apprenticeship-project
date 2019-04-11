from django.db import models

from healthid.utils.app_utils.id_generator import id_gen


class Timezone(models.Model):

    name = models.CharField(max_length=244, unique=True)
    time_zone = models.CharField(
        max_length=244, unique=True)

    def __str__(self):
        return self.time_zone


class Preference(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    outlet_timezone = models.ForeignKey(
        Timezone, on_delete=models.CASCADE)
