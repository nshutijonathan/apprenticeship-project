from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import set_price_string


class TestSetProductPriceTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.product_id1 = self.create_product(product_name='Poison').id
        self.product_id2 = self.create_product(product_name='product').id

    data = {
        'markup': 28,
        'product_ids': '[]',
        'auto_price': 'true',
        'sales_price': 20.32
    }

    def test_set_product_prices_automatically(self):
        self.data['product_ids'] = f'[{self.product_id1}, {self.product_id2}]'
        response = self.query_with_token(
            self.access_token_master,
            set_price_string.format(**self.data)
        )
        self.assertEqual('successfully set prices for products',
                         response['data']['updatePrice']['message'])

    def test_set_product_prices_manually(self):
        self.data['product_ids'] = f'[{self.product_id1}, {self.product_id2}]'
        self.data['auto_price'] = 'false'
        response = self.query_with_token(
            self.access_token_master,
            set_price_string.format(**self.data)
        )
        self.assertEqual('successfully set prices for products',
                         response['data']['updatePrice']['message'])
