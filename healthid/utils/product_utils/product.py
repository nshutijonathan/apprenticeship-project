from graphql import GraphQLError
from healthid.utils.app_utils.database import SaveContextManager
from django.conf import settings


def set_attributes(product, **kwargs):
    tags = kwargs.get("tags")
    kwargs.pop("tags")
    for (key, value) in kwargs.items():
        if type(value) is str and value.strip() == "":
            raise GraphQLError("The {} field can't be empty".format(key))
        if key == 'product_name':
            params = {
                'model_name': 'Product',
                'field': 'product_name',
                'value': value
            }
        if key == 'id':
            continue
        setattr(product, key, value)
    with SaveContextManager(product, **params):
        product.tags.set(*tags)
        return product


def generate_reorder_points_and_max(product_instance):
    """
        this fuction generates reorder points and reorder
        max basing on the weekly average unit sales of a product

    """
    average_weekly_sales = settings.MOCK_AVERAGE_WEEKLY_SALES
    reorder_point = average_weekly_sales * 3
    reorder_max = average_weekly_sales * 6
    product_instance.reorder_point = reorder_point
    product_instance.reorder_max = reorder_max
    product_instance.save()
