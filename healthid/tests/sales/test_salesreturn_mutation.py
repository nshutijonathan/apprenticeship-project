from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales_return import\
    initiate_sales_return_query
from healthid.tests.factories import SaleFactory, OutletFactory, ProductFactory
from datetime import timedelta


class TestCreateSaleReturn(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.sale = SaleFactory()
        self.outlet = OutletFactory()
        self.product = ProductFactory()
        self.sales_return_data = {
            'outlet_id': self.outlet.id,
            'product_id': self.product.id,
            'sale_id': self.sale.id
        }

    def test_initiate_sales_return_success(self):
        """
        test sales return initiation success
        """
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('data', resp)
        self.assertEqual(
            resp['data']['initiateSalesReturn']['message'],
            "Return was initiated successfully"
        )

    def test_initiate_sales_return_wrong_sale(self):
        """
        test sales return initiation failure with wrong sale id
        """
        self.sales_return_data['outlet_id'] = 0
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'],
            "Outlet with id 0 does not exist."
        )

    def test_initiate_sales_return_wrong_product(self):
        """
        test sales return initiation failure with non existing product
        """
        self.sales_return_data['product_id'] = 0
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'],
            "There are no Product(s) matching IDs: 0."
        )

    def test_returnable_days(self):
        """
        test sales return initiation failure due to
        return after 30 default preferred returnable days
        """
        sale = self.sale
        sale.created_at = sale.created_at - timedelta(days=40)
        sale.save()
        self.sales_return_data['sale_id'] = sale.id
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertEqual(
            resp['errors'][0]['message'],
            'Product preferred returnable days are done')
