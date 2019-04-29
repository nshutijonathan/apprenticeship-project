from graphql import GraphQLError
from healthid.utils.app_utils.database import SaveContextManager


def set_attributes(product, **kwargs):
    tags = kwargs.get("tags")
    kwargs.pop("tags")
    for (key, value) in kwargs.items():
        if type(value) is str and value.strip() == "":
            raise GraphQLError("The {} field can't be empty".format(key))
        if key == 'product_name':
            params = {'model_name': 'Product',
                      'field': 'product_name', 'value': value}
        if key == 'id':
            continue
        setattr(product, key, value)
    with SaveContextManager(product, **params):
        product.tags.set(*tags)
        return product
