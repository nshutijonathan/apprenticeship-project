from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.notifications.models import Notification
from healthid.utils.app_utils.database import SaveContextManager


def notify(users, message, subject=None, html_body=None):
    '''Function to notify the appropriate user
    '''
    notification = Notification(message=message)
    with SaveContextManager(notification) as notification:
        for user in users:
            notification.recipient.add(user)
            notification.save()
            if html_body and subject:
                send_email_notifications(subject, user, html_body)


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


def send_email_notifications(subject, user, html_body=None):
    '''Function to send email notifications
    '''
    if user.email_notification_permissions and html_body:
        send_email_to(subject, str(user.email), html_body)
