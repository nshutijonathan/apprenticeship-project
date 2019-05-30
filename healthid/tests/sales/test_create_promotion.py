from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import (create_promotion,
                                                create_promotion_type)


class TestCreatePromotion(TestPromotion):
    def setUp(self):
        super().setUp()

    def test_manager_can_create_a_promotion(self):
        self.promotion_data['title'] = 'new promo'
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIn('success', response['data']['createPromotion'])
        self.assertNotIn('errors', response)

    def test_cannot_create_promotion_without_required_fields(self):
        self.promotion_data['title'] = ''
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'title is required.')

    def test_cannot_create_promotion_with_same_title(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'Promotion with title another promo already exists.')

    def test_only_manager_admin_can_create_promotion(self):
        self.business.user.add(self.user)
        response = self.query_with_token(self.access_token,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])

    def test_cannot_create_promotion_for_outlet_you_dont_belong_to(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'You don\'t belong to outlet with id '
                         f'{self.outlet.id}.')

    def test_cannot_create_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])

    def test_manager_can_create_a_promotion_type(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type('Monthly'))
        self.assertIn('success', response['data']['createPromotionType'])
        self.assertNotIn('errors', response)

    def test_cannot_create_promotion_type_without_required_fields(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type(''))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'Please provide promotion type name.')

    def test_cannot_create_promotion_type_with_same_name(self):
        self.query_with_token(self.access_token_master,
                              create_promotion_type('Monthly'))
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type('Monthly'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'PromotionType with name Monthly already exists.'
                         )
