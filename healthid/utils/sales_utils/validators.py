import json
from graphql import GraphQLError
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.products.models import Product


def validate_fields(promotion, **kwargs):
    for key, value in kwargs.items():
        if type(value) is str and value.strip() == "":
            raise GraphQLError('{} is required.'.format(key))
        if key == 'discount' and (value <= 0 or value > 100):
            raise GraphQLError(
                'discount must be greater than 0 but less than or equal to 100'
            )
        setattr(promotion, key, value)
    return promotion


def check_all_products_exist(product_ids):
    products = []
    for product_id in product_ids:
        product = get_model_object(Product, 'id', product_id)
        if not product.is_approved:
            raise GraphQLError(
                f'Product with id {product_id} hasn\'t been approved yet.'
            )
        products.append(product)
    return products


def add_products_to_promotion(promotion, product_ids):
    products = check_all_products_exist(product_ids)
    for product in products:
        promotion.products.add(product)
    return promotion


def remove_quotes(dictionary):
    """
    Remove quotes from dictionary
    """
    return json.dumps(dictionary).replace('"', "")
