from django.core.management import call_command
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import (
    backup_supplier, create_product, product_query, supplier_mutation)


class TestCreateProduct(BaseConfiguration):
    def setUp(self):
        super().setUp()
        call_command('loaddata', 'healthid/fixtures/product_test')
        self.supplier1 = self.query_with_token(self.access_token,
                                               supplier_mutation)
        self.supplier2 = self.query_with_token(self.access_token,
                                               backup_supplier)
        self.supplier_id = self.supplier1['data']['addSupplier']['supplier'][
            'id']
        self.backup_id = self.supplier2['data']['addSupplier']['supplier'][
            'id']

    def test_create_product(self):
        """method for creating a product"""
        response = self.query_with_token(
            self.access_token,
            create_product.format(
                supplier_id=self.supplier_id, backup_id=self.backup_id))
        self.assertIn('data', response)

    def test_already_existing_productname(self):
        """method tests for an already existing productname """
        self.query_with_token(
            self.access_token,
            create_product.format(
                supplier_id=self.supplier_id, backup_id=self.backup_id))
        response = self.query_with_token(
            self.access_token,
            create_product.format(
                supplier_id=self.supplier_id, backup_id=self.backup_id))
        self.assertIn('errors', response)

    def test_product_query(self):
        response = self.query_with_token(self.access_token, product_query)
        self.assertIn('data', response)
