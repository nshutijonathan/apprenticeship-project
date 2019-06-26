from itertools import compress

from graphql import GraphQLError

from healthid.apps.products.models import Product
from healthid.utils.app_utils.query_objects import GetObjectList


class SalesValidator:

    def __init__(self, products):
        self.product_quantities = []
        self.product_discounts = []
        self.product_prices = []
        self.product_ids = []
        for product in products:
            self.product_ids.append(product['product_id'])
            self.product_quantities.append(product['quantity'])
            self.product_discounts.append(product['discount'])
            self.product_prices.append(product['price'])
        self.product_queryset = self.get_products()
        self.products_db_ids = self.product_queryset.values_list(
            'id', flat=True)

        self.sorted_queryset = sorted(
            self.product_queryset, key=lambda x: self.product_ids.index(x.id))

        self.products_db_quantity = [
            product.quantity for product in self.sorted_queryset]

    def get_products(self):
        message = "Sale must have at least 1 product"
        product_queryset = GetObjectList.get_objects(
            Product, self.product_ids, message)
        return product_queryset

    def check_validity_of_ids(self):
        is_valid = [
            product_id in self.products_db_ids for product_id in
            self.product_ids]

        if not all(is_valid):
            invalid_items = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = 'Products with ids {} do not exists'.format(
                ",".join(map(str, invalid_items)))
            raise GraphQLError(message)

    def check_validity_quantity_sold(self):
        message = "Products with ids '{}' do not have enough quantities to be sold"  # noqa
        is_valid = [(existing_quantity >= requested_quantity) and
                    (requested_quantity > 0) for existing_quantity,
                    requested_quantity in
                    zip(self.products_db_quantity, self.product_quantities)]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.product_ids, [not item for item in is_valid]))

            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

        return self.sorted_queryset

    def check_product_price(self):
        message = "Price for products with ids '{}' should be positive integer"
        is_valid = [price > 1 for price in self.product_prices]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

    def check_product_discount(self):
        message = "Discount with ids '{}' can't have negative values"
        is_valid = [discount >= 1 and discount <=
                    100 for discount in self.product_discounts]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

    def check_sales_fields_validity(self, **kwargs):
        discount_total = kwargs.get('discount_total')
        sub_total = kwargs.get('sub_total')
        amount_to_pay = kwargs.get('amount_to_pay')
        paid_amount = kwargs.get('paid_amount')
        change_due = kwargs.get('change_due')
        if discount_total < 0 or discount_total > 100:
            raise GraphQLError(
                "Discount must be greater between 0 and 100")

        if amount_to_pay < 1 or sub_total < 1:
            raise GraphQLError(
                "Amount should be greater than 1")

        if change_due < 1:
            raise GraphQLError(
                "The Change due should be greater than 1")

        if paid_amount < 1:
            raise GraphQLError(
                "The paid amount should be greater than 1")
