from django.apps import AppConfig


class DespatchQueueConfig(AppConfig):
    name = 'healthid.apps.despatch_queue'

    def ready(self):
        from healthid.jobs.main_job import queue_emails_job
        queue_emails_job()
