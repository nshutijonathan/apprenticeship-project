from django.db import models

from healthid.apps.authentication.models import User
from healthid.utils.app_utils.id_generator import id_gen
from django.db.models.signals import post_save
from healthid.settings import pusher


class Notification(models.Model):
    '''Model to handle all notifications
    '''
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    recipient = models.ManyToManyField(User)
    message = models.TextField(null=False)
    event_name = models.CharField(
        max_length=100, default='general_notification')
    read_status = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)


def save_notify(sender, instance, **kwargs):
    pusher.trigger(
        'notification-channel',
        instance.event_name, {'message':  instance.message})


post_save.connect(save_notify, Notification)
