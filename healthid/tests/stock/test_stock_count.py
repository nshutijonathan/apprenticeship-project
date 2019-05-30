from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.stock import (
    initate_stock_count_query, no_variance_reason_query,
    update_stock_count_query, all_stock_counts, single_stock_count,
    delete_stock_batch
)


class TestStockCount(BaseConfiguration):
    """
    Testing Initiating stock count
    """

    def setUp(self):
        super().setUp()
        self.stock_template = self.create_stock_template()
        self.stock_data = {
            'batchInfo': self.batch_info.id,
            'product': self.product.id,
            'quantityCounted': 10,
            'stockTemplateId': self.stock_template.id,
            'varianceReason': 'IncorrectInitialEntry'
        }
        self.stock_count = self.query_with_token(
            self.access_token,
            initate_stock_count_query.format(**self.stock_data))
        self.stock_count_id = \
            self.stock_count['data']['initiateStock']['stockCount']['id']

    def test_initiate_count(self):
        """
        test stock count creation
        """
        resp = self.query_with_token(
            self.access_token,
            initate_stock_count_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['initiateStock']['errors'], None)
        self.assertEqual(resp['data']['initiateStock']
                         ['stockCount']['product']['productName'],
                         self.product.product_name)

    def test_no_variance_reason(self):
        """
        test no variance reason
        """
        self.stock_data['varianceReason'] = 'NoVariance'
        resp = self.query_with_token(
            self.access_token,
            initate_stock_count_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertIn("There is a variance, Kindly state the variance reason",
                      resp['errors'][0]['message'])

    def test_other_reason(self):
        """
        test no specify reason when using others
        """
        self.stock_data['varianceReason'] = 'Others'
        resp = self.query_with_token(
            self.access_token, no_variance_reason_query.format(
                **self.stock_data))
        self.assertIn('data', resp)
        self.assertIn("Specify the variance reason",
                      resp['errors'][0]['message'])

    def test_update_stock_count(self):
        """
            test update stock count
        """
        self.stock_data['stockCountId'] = self.stock_count_id
        self.stock_data['isCompleted'] = 'false'
        resp = self.query_with_token(
            self.access_token_master,
            update_stock_count_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['updateStock']['errors'], None)
        self.assertEqual(resp['data']['updateStock']
                         ['stockCount']['id'], self.stock_count_id)

    def test_save_in_progress(self):
        """
            test save in progress
        """
        self.stock_data['stockCountId'] = self.stock_count_id
        self.stock_data['isCompleted'] = 'false'
        resp = self.query_with_token(
            self.access_token_master,
            update_stock_count_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['updateStock']['errors'], None)

    def test_send_for_approval(self):
        """
            test send for approval
        """
        self.stock_data['stockCountId'] = self.stock_count_id
        self.stock_data['isCompleted'] = 'true'
        resp = self.query_with_token(
            self.access_token_master,
            update_stock_count_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['updateStock']['errors'], None)

    def test_invalid_quantity(self):
        """
            test invalid quantity
        """
        self.stock_data['quantityCounted'] = -10
        resp = self.query_with_token(
            self.access_token,
            no_variance_reason_query.format(**self.stock_data))
        self.assertIn('data', resp)
        self.assertIn(
            f"Quantity Counted for batch {self.batch_info} "
            f"cannot be less than Zero (0)",
            resp['errors'][0]['message'])

    def test_all_stock_count(self):
        resp = self.query_with_token(
            self.access_token,
            all_stock_counts)
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['stockCounts'][0]
                         ['id'], self.stock_count_id)

    def test_single_stock_count(self):
        stock_count_id = {
            'stockCountId': self.stock_count_id
        }
        resp = self.query_with_token(
            self.access_token,
            single_stock_count.format(**stock_count_id))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['stockCount']
                         ['id'], self.stock_count_id)

    def test_remove_stock_batch(self):
        data = {
            'batchInfo': self.batch_info.id,
            'stockCountId': self.stock_count_id
        }
        resp = self.query_with_token(
            self.access_token,
            delete_stock_batch.format(**data))
        self.assertIn('data', resp)
        self.assertIn(
            "Stock must contain at least (one) 1 batch",
            resp['errors'][0]['message'])