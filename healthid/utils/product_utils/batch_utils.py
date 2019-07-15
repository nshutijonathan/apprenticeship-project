import datetime
from functools import wraps
from itertools import compress

from graphql import GraphQLError


class ProductBatchInfo:
    """
    This class contains methods to help with validating batch info.
    """

    def validate_date_field(self, date_string, date_field):
        date_format = '%Y-%m-%d'
        try:
            datetime.datetime.strptime(date_string, date_format)
        except Exception:
            raise GraphQLError(
                f"Incorrect data format for "
                f"{date_field}, should be YYYY-MM-DD"
            )

    def validate_positive_integers(self, integer, field):
        if integer <= 0:
            raise GraphQLError(
                f"Input a positive number, {field} cannot be less than 1")

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            date_fields = ('date_received', 'expiry_date')
            int_fields = ('quantity_received', 'unit_cost')
            for field, field_value in kwargs.items():
                if field in date_fields:
                    self.validate_date_field(field_value, field)
                if field in int_fields:
                    self.validate_positive_integers(field_value, field)
            return func(*args, **kwargs)
        return wrapper


def check_validity_of_ids(user_inputs, db_ids, message=None):

    is_valid = [user_input in db_ids for user_input in user_inputs]

    if not all(is_valid):
        invalid_items = list(
            compress(user_inputs, [not item for item in is_valid]))
        if message is None:
            message = "Products with ids '{}' do not exist in this batch"

        message = message.format(",".join(map(str, invalid_items)))
        raise GraphQLError(message)


def check_validity_of_quantity(user_inputs, db_quantities, batch_ids):

    is_valid = [user_input < db_quantity for user_input,
                db_quantity in zip(user_inputs, db_quantities)]

    if not all(is_valid):
        invalid_quantities = list(
            compress(user_inputs, [not item for item in is_valid]))
        invalid_product_ids = list(
            compress(batch_ids, [not item for item in is_valid]))
        message = f"Can't transfer batches with ids {invalid_product_ids} \
since quantities {invalid_quantities} are above the available quantity!"

        raise GraphQLError(message)


batch_info_instance = ProductBatchInfo()
