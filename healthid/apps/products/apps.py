from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'healthid.apps.products'

    def ready(self):
        from . import signals  # noqa F401
