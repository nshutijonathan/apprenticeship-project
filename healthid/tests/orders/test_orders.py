from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (order, approve_order,
                                                 edit_order)


class TestOrders(BaseConfiguration):
    '''Class to test orders operations
    '''

    def test_initiate_order(self):
        '''Method to test that users can be able to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, order.format(outlet_id=self.outlet.id))
        self.assertNotIn('errors', response)

    def test_admin_approv_orders(self):
        """Test an admin can approve orders"""
        response = self.query_with_token(
            self.access_token_master,
            approve_order.format(order_id=self.order.id))
        self.assertNotIn('errors', response)

    def test_edit_initiated_order(self):
        '''Method to test that users can be edit to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, edit_order.format(outlet_id=self.outlet.id,
                                                 order_id=self.order.id))
        self.assertNotIn('errors', response)
