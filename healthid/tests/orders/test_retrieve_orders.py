from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (
    retrieve_orders, retrieve_order, retrieve_open_orders,
    retrieve_closed_orders)


class TestRetrieveOrders(BaseConfiguration):
    def test_user_can_retrieve_orders(self):
        response = self.query_with_token(self.access_token, retrieve_orders)
        self.assertIsNotNone(response['data']['orders'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_single_order(self):
        response = self.query_with_token(
            self.access_token, retrieve_order.format(order_id=self.order.id))
        self.assertIsNotNone(response['data']['order'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_open_orders(self):
        response = self.query_with_token(
            self.access_token, retrieve_open_orders)
        self.assertIsNotNone(response['data']['openOrders'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_closed_orders(self):
        response = self.query_with_token(
            self.access_token, retrieve_closed_orders)
        self.assertIsNotNone(response['data']['closedOrders'])
        self.assertNotIn('errors', response)
