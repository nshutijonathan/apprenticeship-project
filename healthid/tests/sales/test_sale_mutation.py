
from faker import Faker
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import (create_sale,
                                                query_sales_history,
                                                query_sale_history)
from healthid.utils.sales_utils.validators import remove_quotes
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.tests.factories import (OutletFactory, SaleFactory,
                                      CustomerFactory, ProductFactory,
                                      BatchInfoFactory, QuantityFactory)

faker = Faker()


class TestCreateSale(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.outlet_2 = OutletFactory()
        self.customer_2 = CustomerFactory()
        self.sale = SaleFactory(outlet=self.outlet_2, customer=self.customer_2)
        self.product_2 = ProductFactory()
        self.product_batch = BatchInfoFactory(product=self.product_2)
        self.quantity_2 = QuantityFactory(quantity_remaining=200,
                                          batch=self.product_batch)
        self.product_details = {"productId": self.product_2.id,
                                "quantity": faker.random_int(min=1, max=5),
                                "discount": faker.random_int(min=0, max=10),
                                "price": faker.random_int(min=10, max=40)}
        self.sales_data = {
            "discount_total": faker.random_int(min=1, max=100),
            "amount_to_pay": faker.random_int(min=1, max=10000),
            "change_due": faker.random_int(min=0, max=10000),
            "paid_amount": faker.random_int(min=0, max=10000),
            "payment_method": "cash",
            "outlet_id": self.outlet.id,
            "customer_id": self.customer_2.id,
            "sub_total": faker.random_int(min=1, max=10000),
            "products": '[{}]'.format(remove_quotes(self.product_details))
        }

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
                         "The Change due should not be less than 0")

    def test_invalid_paid_amount(self):
        self.sales_data["paid_amount"] = -590
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "The paid amount should be greater than 1")

    def test_non_existing_product(self):
        self.product_details["productId"] = 10000
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES['no_matching_ids']
                         .format('Product', 10000))

    def test_invalid_product_discount(self):
        self.product_details["discount"] = -12
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['negative_discount']
                         .format(self.product_2.id))

    def test_less_stock_than_actual_sale(self):
        self.product_details["quantity"] = 500
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['less_quantities']
                         .format(self.product_2.id))

    def test_invalid_price(self):
        self.product_details["price"] = -21
        self.sales_data['products'] = remove_quotes(self.product_details)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['negative_integer']
                         .format(self.product_2.id))

    def test_create_sale_successfully(self):
        self.create_receipt_template()
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertEqual(response['data']['createSale']['message'],
                         "Sale was created successfully")

    def test_fetch_sales_history(self):
        response = self.query_with_token(
            self.access_token_master, query_sales_history(self.outlet_2.id))
        self.assertEqual(self.sale.discount_total, response['data']
                         ['outletSalesHistory'][0]['discountTotal'])

    def test_fetch_sale_history(self):
        response = self.query_with_token(
            self.access_token_master, query_sale_history(self.sale.id))
        self.assertEqual(
            str(self.sale.id), response['data']['saleHistory']['id'])
        self.assertEqual(self.sale.change_due, response['data']
                         ['saleHistory']['changeDue'])
