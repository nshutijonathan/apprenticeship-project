import os

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from healthid.apps.stock.models import StockCountTemplate

from healthid.utils.product_utils.batch_expiries import \
    notify_about_expired_products
from healthid.utils.stock_utils.stock_count_alert import \
    generate_stock_counts_notifications, schedule_templates
from healthid.utils.product_utils.product_expiry import \
    check_for_expiry_products
from healthid.utils.orders_utils.inventory_notification import \
    inventory_check

time_interval = os.environ.get('EXPIRY_NOTIFICATION_DURATION', '43200')
job_run_interval = int(settings.STOCK_JOB_TIME_INTERVAL)
generate_promotion_interval = os.environ.get('GENERATE_PROMOTION_INTERVAL',
                                             1440)

sched = BackgroundScheduler()


@receiver(post_save, sender=StockCountTemplate)
def start_job(sender, instance, **kwargs):
    """
    Triggers job scheduling on the first mutation
    stocktemplate
    """
    if 'created' in kwargs:
        if not kwargs['created'] and instance.unique:
            start_schedule_templates()


def start():
    """
    Method to start the scheduled jobs
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_about_expired_products, 'interval',
                      minutes=int(time_interval))
    scheduler.add_job(check_for_expiry_products,
                      'interval',
                      minutes=int(generate_promotion_interval))
    scheduler.add_job(inventory_check, 'cron',
                      day_of_week='sun',
                      hour=23,
                      minute=50)
    scheduler.start()


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
