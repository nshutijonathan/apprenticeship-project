import csv

from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models import PaymentTerms, Suppliers, Tier
from healthid.apps.outlets.models import City
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)


class AddSupplier:
    def __init__(self):
        self.exclude_list = [
            'DoesNotExist', '_meta', 'MultipleObjectsReturned', 'city', 'tier',
            'payment_terms', 'supplier_id', 'id', 'objects', 'prefered',
            'backup', 'is_approved', 'user_id', 'user', 'admin_comment',
            'parent_id', 'parent', 'proposedEdit', 'batchinfo_set',
            'suppliernote_set', 'supplier_prices'
        ]
        self.safe_list = [
            each for each in Suppliers.__dict__
            if not each.startswith('__') and each not in self.exclude_list
        ]

    @staticmethod
    def create_supplier(user, instance, input):
        params = {'model_name': 'Suppliers',
                  'field': 'email', 'value': input.email}
        for (key, value) in input.items():
            setattr(instance, key, value)
        instance.user = user
        with SaveContextManager(instance, **params):
            pass

    def handle_csv_upload(self, user, io_string):
        for column in csv.reader(io_string, delimiter=','):
            if len(self.safe_list) != len(column):
                message = {"error": "Missing column(s)"}
                raise ValidationError(message)
            dict_object = dict(zip(self.safe_list, column))
            instance = Suppliers()
            for (key, value) in dict_object.items():
                error_type = {'error_type': NotFound}
                if key == 'email':
                    params = {'model_name': Suppliers, 'field': 'email',
                              'value': value, 'error_type': ValidationError}
                if key == 'rating':
                    value = int(value)
                if key == 'city_id':
                    city = get_model_object(
                        City, 'name', value.title(), **error_type)
                    value = city.id
                if key == 'tier_id':
                    tier = get_model_object(
                        Tier, 'name', value.lower(), **error_type)
                    value = tier.id
                if key == 'payment_terms_id':
                    pay_term = get_model_object(
                        PaymentTerms, 'name', value.lower(), **error_type)
                    value = pay_term.id
                setattr(instance, key, value)
            instance.user = user
            with SaveContextManager(instance, **params):
                pass


add_supplier = AddSupplier()
