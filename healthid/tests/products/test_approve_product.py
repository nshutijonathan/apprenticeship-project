from django.core.management import call_command
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures import products


class ApproveProducts(BaseConfiguration):
    def setUp(self):
        super().setUp()
        call_command('loaddata', 'healthid/fixtures/product_csv')
        self.backup_id = 1,
        self.supplier_id = 1,
        self.product = self.query_with_token(self.access_token,
                                             products.create_proposed_product)

    def test_approve_product(self):
        """method for approving a product succesflully """
        product_id = self.product['data']['createProduct']['product']['id']
        response = self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=product_id))
        self.assertIn("success", response["data"]["approveProduct"])
        self.assertNotIn("errors", response)
        self.assertIn(f"Product {product_id} has successfully been approved.",
                      response['data']["approveProduct"]["success"])

    def test_approve_product_with_invalid_id(self):
        """test for approving  product with invalid id """
        invalid_id = 10
        response = self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=invalid_id))
        self.assertNotIn("success", response)
        self.assertIn("errors", response)
        self.assertIn(f"The product with Id {invalid_id} doesn't exist",
                      response['errors'][0]['message'])

    def test_approve_already_approved_product(self):
        """method for approving an already approved product"""
        product_id = self.product['data']['createProduct']['product']['id']
        self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=product_id))
        response = self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=product_id))
        self.assertIn(f"Product {product_id} has already been approved",
                      response['errors'][0]['message'])
        self.assertIn('errors', response)
