from django.core.management import call_command
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures import products
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class ApproveProducts(BaseConfiguration):
    def setUp(self):
        super().setUp()
        call_command('loaddata', 'healthid/fixtures/product_csv')
        self.supplier = self.query_with_token(self.access_token_master,
                                              products.supplier_mutation)
        self.supplier_id = self.supplier['data']['addSupplier']['supplier'][
            'id']
        self.backup_id = self.supplier['data']['addSupplier']['supplier'][
            'id'],
        self.product = self.query_with_token(self.access_token,
                                             products.create_proposed_product
                                             .format(self.supplier_id))

    def test_approve_product(self):
        """method for approving a product successfully """
        product_id = self.product['data']['createProduct']['product']['id']
        response = self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=product_id))
        self.assertIn("success", response["data"]["approveProduct"])
        self.assertNotIn("errors", response)
        self.assertIn(SUCCESS_RESPONSES[
                      "approval_success"].format("Product " + product_id),
                      response['data']["approveProduct"]["success"])

    def test_approve_product_with_invalid_id(self):
        """test for approving  product with invalid id """
        invalid_id = 1000
        response = self.query_with_token(
            self.access_token_master,
            products.approve_product.format(product_id=invalid_id))
        self.assertNotIn("success", response)
        self.assertIn("errors", response)
        self.assertIn("Product with id 1000 does not exist.",
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
        self.assertIn(PRODUCTS_ERROR_RESPONSES[
                      "product_approval_duplication"].format(product_id),
                      response['errors'][0]['message'])
        self.assertIn('errors', response)
