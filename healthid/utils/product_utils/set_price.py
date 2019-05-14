from django.db.utils import DatabaseError, OperationalError


class SetPrice:
    """This class handles setting prices to a group
    of products
    """

    def __init__(self):
        self.errors = []
        self.products = []

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
