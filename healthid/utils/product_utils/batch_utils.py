import datetime
from functools import wraps
from graphql import GraphQLError
from healthid.utils.product_utils.product_querysets import \
    ProductModelQuery


class ProductBatchInfo:
    """
    This class contains methods to help with updating of user details.
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

    def validate_postive_integers(self, integer, field):
        if integer <= 0:
            raise GraphQLError(
                f"Input a postive number, {field} cannot be less than 1")

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            date_fields = ('date_received', 'expiry_date')
            int_fields = ('quantity_received', 'unit_cost')
            for field in kwargs.keys():
                field_value = kwargs.get(field)
                if field in date_fields:
                    self.validate_date_field(field_value, field)
                if field == 'batch_id':
                    ProductModelQuery().query_batch_info(field_value)
                if field == 'supplier_id':
                    ProductModelQuery().query_supplier_id(field_value)
                if field == 'product':
                    if len(field_value) < 1:
                        raise GraphQLError('This batch must be have '
                                           'to at least 1 (one) Product')
                    for product in field_value:
                        ProductModelQuery().query_product_id(product)
                if field in int_fields:
                    self.validate_postive_integers(field_value, field)
            return func(*args, **kwargs)
        return wrapper


batch_info_instance = ProductBatchInfo()
