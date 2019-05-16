import os

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from healthid.utils.product_utils.batch_expiries import \
    notify_about_expired_products
from healthid.utils.stock_utils.stock_count_alert import \
    generate_stock_counts_notifications

time_interval = os.environ.get('EXPIRY_NOTIFICATION_DURATION', '43200')
job_run_interval = int(settings.STOCK_JOB_TIME_INTERVAL)


def start():
    '''Method to start the scheduled jobs
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_about_expired_products, 'interval',
                      minutes=int(time_interval))
    scheduler.start()


def alert_counting():
    '''Method starts a new job for stock counts notifications
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        generate_stock_counts_notifications, 'interval',
        minutes=job_run_interval)
    scheduler.start()
