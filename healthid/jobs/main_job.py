import os
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.date_utils.is_same_date import \
    (remove_microseconds, remove_seconds)
from healthid.utils.despatch_util.despatch_email_util import (
    resend_emails, send_email_notifications)
from healthid.apps.stock.models import StockCountTemplate
from healthid.apps.despatch_queue.models import DespatchQueue, Despatch_Meta

from healthid.utils.product_utils.batch_expiries import \
    notify_about_expired_products, notify_pusher_about_expired_products
from healthid.utils.stock_utils.stock_count_alert import \
    generate_stock_counts_notifications, schedule_templates
from healthid.utils.product_utils.product_expiry import \
    check_for_expiry_products
from healthid.utils.orders_utils.inventory_notification import \
    inventory_check
from django.utils import timezone

time_interval = os.environ.get('EXPIRY_NOTIFICATION_DURATION', '43200')
job_run_interval = int(settings.STOCK_JOB_TIME_INTERVAL)
generate_promotion_interval = os.environ.get('GENERATE_PROMOTION_INTERVAL',
                                             1440)

sched = BackgroundScheduler()

scheduler = BackgroundScheduler()
scheduler.add_job(notify_about_expired_products,
                  'interval', minutes=int(time_interval))
scheduler.add_job(check_for_expiry_products, 'interval',
                  minutes=int(generate_promotion_interval))
scheduler.add_job(inventory_check, 'cron',
                  day_of_week='sun', hour=23, minute=50)
scheduler.add_job(notify_pusher_about_expired_products, 'cron',
                  day_of_week='mon', hour=9, minute=30)
scheduler.add_job(notify_pusher_about_expired_products, 'cron',
                  day_of_week='mon', hour=9, minute=30)
scheduler.add_job(resend_emails, 'cron', day_of_week='wed',
                  hour=8, minute=30)


def queue_emails_job():
    sched = BackgroundScheduler()
    email_parts = {}
    try:
        despatch_queue = DespatchQueue.objects.all()
        despatch_queue_meta = Despatch_Meta.objects.all()
        if len(despatch_queue) > 0:
            for despatch_q in despatch_queue:
                id = despatch_q.recipient_id
                if remove_seconds(despatch_q.due_date) <= \
                        remove_seconds(
                            remove_microseconds(timezone.now())) and \
                        despatch_q.status == 'pending':
                    email_part = get_model_object(User, 'id', id)
                    for despatch_meta in despatch_queue_meta:
                        if despatch_meta.__dict__['despatch_id'] ==\
                                despatch_q.__dict__['id']:
                            email_parts['email'] = email_part
                            email_parts[despatch_meta.__dict__['dataKey']
                                        ] = despatch_meta.__dict__['dataValue']
                    if email_parts:
                        sched.add_job(send_email_notifications, trigger='date',
                                      next_run_time=str(
                                          remove_seconds(despatch_q.due_date)),
                                      args=[
                                          email_parts['subject'],
                                          email_parts['email'],
                                          email_parts['body'], despatch_meta]
                                      )
                        sched.start()
    except Exception:
        pass


def alert_counting():
    """
    Method starts a new job for stock counts notifications
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        generate_stock_counts_notifications, 'interval',
        minutes=job_run_interval)
    scheduler.start()


def start_schedule_templates():
    """
    Shedules a job for each of the template filtered
    """
    if not sched.state:
        sched.start()

    stock_templates = StockCountTemplate.objects.filter(
        scheduled=False, interval__gt=0)
    for template in stock_templates:
        sched.add_job(
            lambda: schedule_templates(template), 'interval',
            id='{}'.format(template.id),
            days=template.interval,
            start_date=template.created_at,
            end_date=template.end_on)
        template.scheduled = True
        template.save()


@receiver(post_delete, sender=StockCountTemplate)
def remove_scheduled_jobs(sender, instance, using, **kwargs):
    """
    Stops a schedule when a template is deleted if necessary
    """
    job_id = '{}'.format(instance.id)
    if sched.get_job(job_id) in sched.get_jobs():
        sched.remove_job(job_id)
