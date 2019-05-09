import os

from apscheduler.schedulers.background import BackgroundScheduler

from healthid.utils.product_utils.batch_expiries import \
    notify_about_expired_products

time_interval = os.environ.get('EXPIRY_NOTIFICATION_DURATION', '43200')


def start():
    '''Method to start the scheduled jobs
    '''
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_about_expired_products, 'interval',
                      minutes=int(time_interval))
    scheduler.start()
