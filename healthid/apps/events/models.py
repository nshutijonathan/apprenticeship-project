from django.db import models
from healthid.apps.outlets.models import Outlet
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.id_generator import id_gen


class EventType(models.Model):
    '''Model to handle event types
    '''
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    '''
    This model handles event data.
    '''
    outlet = models.ManyToManyField(Outlet, blank=True)
    event_type = models.ForeignKey(EventType, null=True, blank=True,
                                   on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    event_title = models.CharField("title", max_length=255)
    description = models.TextField("description", null=True, blank=True)
    user = models.ManyToManyField(User)
