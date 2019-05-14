from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import order


class TestOrders(BaseConfiguration):
    '''Class to test orders operations
    '''

    def test_initiate_order(self):
        '''Method to test that users can be able to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, order.format(outlet_id=self.outlet.id))
        self.assertNotIn('errors', response)
