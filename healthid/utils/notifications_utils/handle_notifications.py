from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.notifications.models import Notification
from healthid.utils.app_utils.database import SaveContextManager


def notify(users, subject, message, html_body):
    '''Function to notify the appropriate user
    '''
    notification = Notification(message=message)
    with SaveContextManager(notification) as notification:
        for user in users:
            notification.recipient.add(user)
            notification.save()

            send_email_notifications(subject, user, html_body)


def send_email_notifications(subject, user, html_body=None):
    '''Function to send email notifications
    '''
    if user.email_notification_permissions and html_body:
        email = EmailMessage(subject=subject,
                             body=html_body,
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             to=[str(user.email)])

        email.content_subtype = 'html'
        email.send()
