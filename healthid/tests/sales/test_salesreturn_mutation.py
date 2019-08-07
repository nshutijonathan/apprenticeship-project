from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales_return import\
    initiate_sales_return_query
from healthid.tests.test_fixtures.customers import create_customer
from healthid.tests.test_fixtures.sales import create_sale
from healthid.utils.sales_utils.validators import remove_quotes
from healthid.apps.sales.models import Sale
from datetime import timedelta


class TestCreateSaleReturn(BaseConfiguration):
    def setUp(self):
        super().setUp()
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        self.customer_id = response["data"]["createCustomer"]['customer']['id']
        self.product_details = {"productId": self.product.id,
                                "quantity": 4, "discount": 0, "price": 21}
        self.sales_data = {
            "discount_total": 48.5,
            "amount_to_pay": 20,
            "change_due": 399,
            "paid_amount": 590,
            "payment_method": "cash",
            "outlet_id": self.outlet.id,
            "customer_id": self.customer_id,
            "sub_total": 33,
            "products": '[{}]'.format(remove_quotes(self.product_details))
        }
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        sale_id = response['data']['createSale']['sale']['id']
        self.sales_return_data = {
            'outlet_id': self.outlet.id,
            'product_id': self.product.id,
            'sale_id': sale_id
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
        del self.sales_data['products']
        self.sales_data['sales_person_id'] = self.user.id
        sale = Sale.objects.create(**self.sales_data)
        sale.created_at = sale.created_at - timedelta(days=40)
        sale.save()
        self.sales_return_data['sale_id'] = sale.id
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertEqual(
            resp['errors'][0]['message'],
            'Product preferred returnable days are done')
