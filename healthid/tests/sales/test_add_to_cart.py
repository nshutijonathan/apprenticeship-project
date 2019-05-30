from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import add_to_cart


class TestCreateCart(BaseConfiguration):
    def test_user_can_add_product_to_cart(self):
        self.product.is_approved = True
        self.product.save()
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(self.product.id, 1))
        self.assertIn('success', response['data']['addToCart'])
        self.assertNotIn('errors', response)

    def test_user_cannot_add_unapproved_product_to_cart(self):
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(self.product.id, 1))
        self.assertEqual(response['errors'][0]['message'],
                         f'{self.product.product_name} isn\'t approved yet.')

    def test_user_cant_add_product_to_cart_with_quantity_than_available(self):
        self.product.is_approved = True
        self.product.save()
        product = self.product
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(product.id,
                                                     product.quantity + 10))
        self.assertEqual(response['errors'][0]['message'],
                         f'There is only quantity {product.quantity} of '
                         f'{product.product_name} available in stock.')

    def test_user_cant_add_product_to_cart_when_unathenticated(self):
        response = self.query_with_token('', add_to_cart(self.product.id, 1))
        self.assertIsNotNone(response['errors'])
