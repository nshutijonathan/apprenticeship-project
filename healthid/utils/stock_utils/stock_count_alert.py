import threading
from datetime import datetime, timedelta

from healthid.apps.notifications.models import Notification
from healthid.apps.stock.models import StockCountTemplate
from healthid.utils.app_utils.database import (SaveContextManager)
from healthid.utils.app_utils.send_mail import SendMail


def generate_stock_counts_notifications():
    '''Method to generate notifications
    '''
    today = datetime.now()
    count_date = today+timedelta(days=1)
    stock_templates = StockCountTemplate.objects.filter(
        schedule_time__start_date__range=(today, count_date))
    if stock_templates:
        for template in stock_templates:
            assigned_users = template.assigned_users.all()
            to_email = assigned_users.values_list('email', flat=True)
            email_stock_template = 'email_alerts/stocks/stock_email.html'
            subject = 'Stock counts alert'
            date = datetime.strftime(
                template.schedule_time.start_date, "%d-%b-%Y")
            messg = f'Reminder for the scheduled stock count on {date}'
            context = {
                'schedule_time': date,
                'template_type': 'Stock counts notification',
                'small_text_detail': messg
            }
            send_mail = SendMail(email_stock_template,
                                 context, subject, to_email)
            thread = threading.Thread(target=notify_users(
                send_mail, assigned_users, messg),
                daemon=True)
            thread.start()


def notify_users(send_mail, assigned_users, message):
    '''
        Method to triger notifications
    '''
    notification = Notification.objects.create(message=message)
    with SaveContextManager(notification) as notification:
        for user in assigned_users:
            notification.recipient.add(user)
    send_mail.send()
