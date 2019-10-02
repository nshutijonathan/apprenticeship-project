from datetime import timezone, datetime
from itertools import compress
from graphql import GraphQLError

from healthid.apps.preference.models import OutletPreference
from healthid.apps.products.models import Product
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


class SalesValidator:
    def __init__(self, products):
        self.product_quantities = []
        self.product_discounts = []
        self.product_prices = []
        self.product_ids = []
        for product in products:
            self.product_ids.append(product['product_id'])
            self.product_quantities.append(product['quantity'])
            self.product_discounts.append(product.get('discount'))
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
        message = SALES_ERROR_RESPONSES['less_quantities']  # noqa
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
        message = SALES_ERROR_RESPONSES['negative_integer']
        is_valid = [price > 1 for price in self.product_prices]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

    def check_product_discount(self):
        message = SALES_ERROR_RESPONSES['negative_discount']
        is_valid = [discount >= 0 and discount <=
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

        if change_due < 0:
            raise GraphQLError(
                "The Change due should not be less than 0")

        if paid_amount < 1:
            raise GraphQLError(
                "The paid amount should be greater than 1")

    def check_payment_method(self, **kwargs):
        payment_method = kwargs.get('payment_method').lower()
        outlet_id = kwargs.get('outlet_id')
        preferences = get_model_object(
            OutletPreference, 'outlet_id', outlet_id)
        message = SALES_ERROR_RESPONSES['invalid_payment']
        if preferences.payment_method == 'both' and \
                payment_method not in ['cash', 'card', 'credit']:
            raise GraphQLError(message)
        if preferences.payment_method != 'both' and \
                payment_method not in ['others', 'credit']:
            if preferences.payment_method != payment_method:
                raise GraphQLError(message)

    def check_product_returnable(self):
        message = message = SALES_ERROR_RESPONSES['not_returnable']
        is_valid = [product.is_returnable for product in self.product_queryset]
        if not all(is_valid):
            invalid_items = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = message.format(
                ",".join(map(str, invalid_items)))
            raise GraphQLError(message)

    def check_product_dates_for_return(self, outlet, sales_instance):
        message = "Product preferred returnable days are done"
        date_of_purchase = sales_instance.created_at
        date_difference = datetime.now(timezone.utc) - date_of_purchase
        date_change = date_difference.days
        if outlet.outletpreference.returnable_days < date_change:
            raise GraphQLError(message)
