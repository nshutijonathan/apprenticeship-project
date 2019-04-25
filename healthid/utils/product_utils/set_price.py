from functools import reduce

from django.db.models import Q
from django.db.utils import DatabaseError, OperationalError

from healthid.apps.products.models import Product


class SetPrice:
    """This class handles setting prices to a group
    of products
    """

    def __init__(self):
        self.errors = []
        self.products = []

    def get_products(self, list_of_ids):
        """Queries the database to return a list of
        product objects

        Arguments:
            list of product ids

        Returns:
            A list of products
        """
        query = reduce(lambda q, id: q | Q(id=id), list_of_ids, Q())
        queryset = Product.objects.filter(query)
        return queryset

    def update_product_price(self, product, **kwargs):
        for (key, value) in kwargs.items():
            if value is not None:
                try:
                    setattr(product, key, value)
                except(DatabaseError, OperationalError) as e:
                    self.errors.append(str(e))
        product.save()
        self.products.append(product)
        return (self.errors, self.products)
