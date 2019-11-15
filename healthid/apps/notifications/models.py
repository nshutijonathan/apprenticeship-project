from django.db import models
from django.db.models.signals import post_save
from healthid.apps.authentication.models import User
from healthid.models import BaseModel
from healthid.settings import pusher
from healthid.utils.app_utils.id_generator import id_gen


class NotificationRecord(BaseModel):
    '''
    Model class to handle notification read status
    and deletion.
    '''
    recipient = models.ForeignKey(
        User, related_name='user_notifications_records',
        on_delete=models.CASCADE)
    read_status = models.BooleanField(default=False)


class Notification(BaseModel):
    '''Model to handle all notifications
    '''
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    message = models.TextField(null=False)
    event_name = models.CharField(
        max_length=100, default='general_notification')
    notification_records = models.ManyToManyField(NotificationRecord,
                                                  related_name='notification')


def save_notify(sender, instance, **kwargs):
    pusher.trigger(
        'notification-channel',
        instance.event_name, {'message':  instance.message})


post_save.connect(save_notify, Notification)
