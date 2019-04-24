from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.batch_expiry import (batch_expiry_query,
                                                       query_expired_products,
                                                       wrong_expiry_date)


class TestBatchInfo(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def test_batch_expire_month(self):
        """
        test expiring batch data by month
        """
        response = self.query_with_token(
            self.access_token, batch_expiry_query)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_wrong_expiry_date(self):
        """
        test wrong expiry date passed in
        """
        response = self.query_with_token(
            self.access_token, wrong_expiry_date)
        self.assertIn('errors', response)

    def test_expired_products(self):
        """
        test expiring batch data by week
        """
        response = self.query_with_token(
            self.access_token, query_expired_products)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)
