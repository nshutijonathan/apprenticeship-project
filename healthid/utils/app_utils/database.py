import re
from django.db import IntegrityError, DatabaseError, OperationalError
from django.core.exceptions import ObjectDoesNotExist

from healthid.utils.app_utils.error_handler import errors


class SaveContextManager():
    '''Manage database exceptions.'''

    def __init__(self, model_instance, **kwargs):
        self.model_instance = model_instance
        self.model_name = kwargs.get('model_name', None)
        self.field = kwargs.get('field', 'name')
        self.value = kwargs.get('value', None)
        self.message = kwargs.get('message', None)
        self.error = kwargs.get('error', None)

    def __enter__(self):
        try:
            self.model_instance.save()
            return self.model_instance
        except IntegrityError as e:
            if 'violates foreign key constraint' in str(e):
                self.model_name, self.value = self.get_model_value(str(e))
                errors.db_object_do_not_exists(
                    self.model_name, 'id', self.value, error_type=self.error)
            if self.message is not None:
                errors.custom_message(self.message, error_type=self.error)
            errors.check_conflict(
                self.model_name, self.field, self.value, error_type=self.error)
        except (DatabaseError, OperationalError) as e:
            message = f'Something went wrong, {str(e)}'
            errors.custom_message(message, error_type=self.error)

    def __exit__(self, exception_type, exception_value, traceback):
        return False

    def get_model_value(self, error):
        model = re.findall(r'[table\s]"[a-zA-Z_]+', error)[-1].split('_')[-1]
        value = re.findall(r'[=(][0-9a-zA-Z]+', error)[-1].replace("(", "")
        return model.capitalize(), value


def get_model_object(model, column_name, column_value, **kwargs):
    '''Gets model instance from db'''
    try:
        model_instance = model.objects.get(**{column_name: column_value})
        return model_instance
    except ObjectDoesNotExist:
        message = kwargs.get('message', None)
        error_type = kwargs.get('error_type', None)
        if message is not None:
            errors.custom_message(message, error_type=error_type)
        errors.db_object_do_not_exists(
            model.__name__, column_name, column_value, error_type=error_type)
