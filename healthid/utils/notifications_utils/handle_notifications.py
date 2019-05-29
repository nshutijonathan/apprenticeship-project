from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.notifications.models import Notification, NotificationRecord
from healthid.utils.app_utils.database import SaveContextManager
from django.template.loader import render_to_string


def notify(users, message, event_name, subject=None, html_body=None):
    '''Function to notify the appropriate user
    '''
    notification = Notification(message=message, event_name=event_name)
    with SaveContextManager(notification) as notification:
        for user in users:
            notification.save()
            notification_record = NotificationRecord.objects.create(
                recipient=user
            )
            notification.notification_records.add(notification_record)
            if html_body and subject:
                send_email_notifications(message, subject, user, html_body)


def send_email_to(subject, email, html_body=None):
    """
    Send email to given address
    """
    email = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    email.content_subtype = 'html'
    email.send()


def send_email_notifications(message, subject, user, html_body=None):
    '''Function to send email notifications
    '''
    if user.email_notification_permissions and html_body:
        html = render_to_string(
            html_body,
            subject
        )
        email = EmailMessage(subject=message,
                             body=html,
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             to=[str(user.email)])

        email.content_subtype = 'html'
        email.send()
