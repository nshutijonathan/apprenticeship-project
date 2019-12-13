from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.authentication.models import User
from healthid.apps.despatch_queue.models import DespatchQueue, Despatch_Meta
from healthid.utils.app_utils.database import SaveContextManager
from django.template.loader import render_to_string
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.date_utils.is_same_date import is_same_date
from smtplib import (
    SMTPException, SMTPAuthenticationError,
    SMTPServerDisconnected, SMTPConnectError)
import threading
import datetime


def notify(users, **kwargs):
    '''Function to notify the users
    through email notifications
    '''
    despatch = {}
    despatch_queues = []
    for user in users:
        despatch_queue = DespatchQueue.objects.create(
            recipient=user,
            due_date=kwargs.get('due_date')
        )
        with SaveContextManager(despatch_queue, model=DespatchQueue)\
                as d_queue:
            body = kwargs.get('body')
            subject = kwargs.get('subject')
            for (key, value) in kwargs.items():
                if key != 'due_date':
                    despatch = Despatch_Meta(
                        dataKey=key, dataValue=value, despatch=d_queue)
                    despatch.save()
            if is_same_date(d_queue.due_date, datetime.datetime.now()):
                try:
                    change_send_status(d_queue, 'processing')
                    thread = threading.Thread(
                        target=send_email_notifications(subject,
                                                        user,
                                                        body),
                        daemon=True)
                    thread.start()
                except (
                        SMTPAuthenticationError,
                        SMTPServerDisconnected,
                        SMTPConnectError):
                    change_send_status(d_queue, 'pending')
                except SMTPException:
                    change_send_status(d_queue, 'failed')
                else:
                    change_send_status(d_queue, 'sent')
            despatch_queues.append(d_queue)
    return despatch_queues


def change_send_status(d_queue, status):
    '''Function to change received status
    '''
    d_queue.status = status
    with SaveContextManager(d_queue, model=DespatchQueue):
        return


def resend_emails():
    email_parts = {}
    despatch_queues = DespatchQueue.objects.all()
    despatch_queue_meta = Despatch_Meta.objects.all()
    if len(despatch_queues) > 0:
        for despatch_q in despatch_queues:
            user_id = despatch_q.recipient_id
            if despatch_q.status == "pending":
                email_part = get_model_object(User, 'id', user_id)
                for despatch_meta in despatch_queue_meta:
                    if despatch_meta.__dict__['despatch_id'] ==\
                            despatch_q.__dict__['id']:
                        email_parts['email'] = email_part
                        email_parts[despatch_meta.__dict__['dataKey']
                                    ] = despatch_meta.__dict__['dataValue']
                if email_parts:
                    try:
                        send_email_notifications(
                            email_parts['subject'],
                            email_parts['email'],
                            email_parts['body'])

                        change_send_status(despatch_meta, 'processing')
                    except (
                            SMTPAuthenticationError,
                            SMTPServerDisconnected,
                            SMTPConnectError):
                        change_send_status(despatch_meta, 'pending')
                    except SMTPException:
                        change_send_status(despatch_meta, 'failed')
                    else:
                        change_send_status(despatch_meta, 'sent')


def send_email_notifications(subject, user, body):
    '''Function to send email notifications
    '''
    template = \
        'email_alerts/email_base.html'
    subject = subject
    context = {
        'template_type': 'Email Notification',
        'small_text_detail': body,
    }
    if user.email_notification_permissions and body:
        html_body = render_to_string(
            template,
            context
        )
        email = EmailMessage(subject=subject,
                             body=html_body,
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             to=[str(user.email)])
        email.content_subtype = 'html'
        email.send()
