from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import (create_product_category)


class TestProductCategory(BaseConfiguration):
    """
    class handles tests for product category
    """

    def test_create_product_category(self):
        """
        test product category creation
        """
        response = self.query_with_token(self.access_token_master,
                                         create_product_category)
        self.assertIn('Product Category created succesfully',
                      response['data']['createProductCategory']['message'])
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_duplicate_product_categopry(self):
        """
        test product category creation
        """
        self.query_with_token(self.access_token_master,
                              create_product_category)
        duplicate_category = self.query_with_token(self.access_token_master,
                                                   create_product_category)
        self.assertIn('ProductCategory with name panadol already exists.',
                      duplicate_category['errors'][0]['message'])
        self.assertIn('errors', duplicate_category)
