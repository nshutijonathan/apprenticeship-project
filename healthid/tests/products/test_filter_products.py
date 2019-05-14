from healthid.tests.products.test_create_product import TestCreateProduct
from healthid.tests.test_fixtures.products import (product_search_query)


class TestFilterProducts(TestCreateProduct):
    def test_empty_search_string(self):
        "method that tests empty user input"
        search_term = ""
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertIn('errors', response)
        self.assertEquals(response['errors'][0]['message'],
                          'Please provide a valid search keyword')

    def test_return_search_result(self):
        "method that tests correct search result is returned"
        search_term = "pan"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)

    def test_nonexistent_product(self):
        "method that tests a product that does not exist"
        search_term = "dry"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))

        self.assertIn('errors', response)
        self.assertEquals(response['errors'][0]['message'],
                          "Product matching search query does not exist")
