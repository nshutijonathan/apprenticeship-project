
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.customers import create_customer
from healthid.tests.test_fixtures.sales import create_sale
from healthid.utils.sales_utils.validators import remove_quotes


class TestCreateSale(BaseConfiguration):
    def setUp(self):
        super().setUp()
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        self.customer_id = response["data"]["createCustomer"]['customer']['id']

        self.product_details = {"productId": self.product.id,
                                "quantity": 4, "discount": 12, "price": 21}
        self.sales_data = {
            "discount_total": 48.5,
            "amount_to_pay": 20,
            "change_due": 399,
            "paid_amount": 590,
            "payment_method": "card",
            "outlet_id": self.outlet.id,
            "customer_id": self.customer_id,
            "sub_total": 33,
            "products": '[{}]'.format(remove_quotes(self.product_details))
        }

    def test_customer_does_not_exist(self):
        self.sales_data["customer_id"] = "89"
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Profile with id 89 does not exist.")

    def test_invalid_discount(self):
        self.sales_data["discount_total"] = -48.5
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Discount must be greater between 0 and 100")

    def test_invalid_amount(self):
        self.sales_data["sub_total"] = -33
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Amount should be greater than 1")

    def test_empty_product_list(self):
        self.sales_data["products"] = []
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Sale must have at least 1 product")

    def test_invalid_change_due(self):
        self.sales_data["change_due"] = -399
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "The Change due should be greater than 1")

    def test_invalid_paid_amount(self):
        self.sales_data["paid_amount"] = -590
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "The paid amount should be greater than 1")

    def test_non_existing_product(self):
        self.product_details["productId"] = 23
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "There are no Product(s) matching IDs: 23.")

    def test_invalid_product_discount(self):
        self.product_details["discount"] = -12
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Discount with ids '{}' can't have negative values"
                         .format(self.product.id))

    def test_less_stock_than_actual_sale(self):
        self.product_details["quantity"] = 179
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Products with ids '{}' do not have enough quantities to be sold"  # noqa
                         .format(self.product.id))

    def test_invalid_price(self):
        self.product_details["price"] = -21
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Price for products with ids '{}' should be positive integer"  # noqa
                         .format(self.product.id))

    def test_create_sale_successfully(self):
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertEqual(response['data']['createSale']['message'],
                         "Sale was created successfully")
