from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import add_quantities, add_suppliers
from healthid.tests.test_fixtures.orders import order as initiate_order
from healthid.tests.test_fixtures.orders import (products_query,
                                                 suppliers_autofill)


class OrderDetailsTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        order = self.query_with_token(
            self.access_token, initiate_order.format(outlet_id=self.outlet.id))
        self.details_dict = {
            'order_id': order['data']['initiateOrder']['order']['id'],
            'product': self.product.id
        }
        self.product.reorder_max = 50
        self.product.reorder_point = 30
        self.product.save()

    def test_suppliers_autofill(self):
        response = self.query_with_token(
            self.access_token, suppliers_autofill.format(**self.details_dict))

        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_add_suppliers(self):
        self.details_dict['supplier'] = self.supplier.id
        response = self.query_with_token(
            self.access_token, add_suppliers.format(**self.details_dict))
        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_add_quantities(self):
        response = self.query_with_token(
            self.access_token, add_quantities.format(**self.details_dict))
        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_query_products_with_low_quantity(self):
        response = self.query_with_token(
            self.access_token, products_query)
        self.assertIsNotNone(response['data']['productAutofill'])
