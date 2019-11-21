
from faker import Faker
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import (create_sale,
                                                query_sales_history,
                                                query_sale_history,
                                                all_sales_history_query,
                                                create_sale_with_empty_batches)
from healthid.utils.messages.sales_responses import (
    SALES_ERROR_RESPONSES, SALES_SUCCESS_RESPONSES)
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.tests.factories import (OutletFactory, SaleFactory,
                                      CustomerFactory, ProductFactory,
                                      BatchInfoFactory, QuantityFactory,
                                      CustomerCreditFactory)

faker = Faker()


class TestCreateSale(BaseConfiguration):
    def setUp(self):
        super(TestCreateSale, self).setUp()
        self.outlet_2 = OutletFactory()
        self.customer_2 = CustomerFactory()
        self.sale = SaleFactory(outlet=self.outlet_2, customer=self.customer_2)
        self.product_2 = ProductFactory()
        self.wallet = CustomerCreditFactory(
            customer=self.customer_2,
            store_credit=500,
            credit_currency=self.currency)
        self.product_batch = BatchInfoFactory(product=self.product_2)
        self.quantity_2 = QuantityFactory(quantity_remaining=200,
                                          batch=self.product_batch)
        self.sales_data = {
            "discount_total": faker.random_int(min=1, max=100),
            "amount_to_pay": faker.random_int(min=1, max=10000),
            "change_due": 7980.0,
            "paid_amount": faker.random_int(min=0, max=10000),
            "payment_method": "cash",
            "outlet_id": self.preference.outlet_id,
            "customer_id": self.customer_2.id,
            "sub_total": faker.random_int(min=1, max=10000),
            "batchId": self.product_batch.id,
            "quantity": faker.random_int(min=1, max=5),
            "discount": faker.random_int(min=0, max=10),
            "price": faker.random_int(min=10, max=40),
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
        response = self.query_with_token(
            self.access_token,
            create_sale_with_empty_batches.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         "Sale must have at least 1 batch")

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

    def test_non_existing_batch(self):
        self.sales_data["batchId"] = 10000
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES['no_matching_ids']
                         .format('BatchInfo', 10000))

    def test_invalid_product_discount(self):
        self.sales_data["discount"] = -12
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['negative_discount']
                         .format(self.sales_data['batchId']))

    def test_less_stock_than_actual_sale(self):
        self.sales_data["quantity"] = 500
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['less_quantities']
                         .format(self.sales_data['batchId']))

    def test_invalid_price(self):
        self.sales_data["price"] = -21
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES['negative_integer']
                         .format(self.sales_data['batchId']))

    def test_create_sale_successfully(self):
        self.create_receipt_template()
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_SUCCESS_RESPONSES["create_sales_success"]
        self.assertNotIn("errors", response)
        self.assertEqual(response['data']['createSale']['message'],
                         message)

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

    def test_fetch_all_sales_history(self):
        response = self.query_with_token(
            self.access_token_master, all_sales_history_query)
        self.assertEqual(str(self.sale.id),
                         response['data']['allSalesHistory'][0]['id'])

    def test_buy_items_with_less_credit(self):
        self.sales_data['payment_method'] = "credit"
        self.sales_data['amount_to_pay'] = faker.random_int(min=600)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_ERROR_RESPONSES['less_credit']
        self.assertEqual(
            response['errors'][0]['message'], message)

    def test_buy_items_with_credit(self):
        self.sales_data['payment_method'] = "credit"
        self.sales_data['amount_to_pay'] = faker.random_int(
            min=1, max=100)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_SUCCESS_RESPONSES["create_sales_success"]
        self.assertNotIn("errors", response)
        self.assertEqual(response['data']['createSale']['message'], message)

    def test_buy_items_with_wrong_credit_currency(self):
        wallet_2 = CustomerCreditFactory()

        sales_data_2 = self.sales_data

        sales_data_2['payment_method'] = "credit"
        sales_data_2['amount_to_pay'] = faker.random_int(
            min=1, max=100)
        sales_data_2['customer_id'] = wallet_2.customer_id
        response = self.query_with_token(
            self.access_token, create_sale.format(**sales_data_2))
        message = SALES_ERROR_RESPONSES['wrong_currency']
        self.assertEqual(response['errors'][0]['message'], message)

    def test_with_negative_pay(self):
        self.sales_data['payment_method'] = "credit"
        self.sales_data['amount_to_pay'] = faker.random_int(
            min=-1000, max=-1)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_ERROR_RESPONSES['invalid_amount']
        self.assertEqual(response['errors'][0]['message'], message)

    def test_with_invalid_discount(self):
        self.sales_data['payment_method'] = "credit"
        self.sales_data['discount_total'] = faker.random_int(
            min=100, max=1000)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_ERROR_RESPONSES['invalid_discount']
        self.assertEqual(response['errors'][0]['message'], message)

    def test_with_invalid_payment_method(self):
        self.sales_data['payment_method'] = "credit-card-cash"
        self.sales_data['amount_to_pay'] = faker.random_int(
            min=1, max=100)
        response = self.query_with_token(
            self.access_token, create_sale.format(**self.sales_data))
        message = SALES_ERROR_RESPONSES['invalid_payment']
        self.assertEqual(response['errors'][0]['message'], message)
