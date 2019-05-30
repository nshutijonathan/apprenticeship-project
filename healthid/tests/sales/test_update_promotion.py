from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import update_promotion


class TestUpdatePromotion(TestPromotion):

    def test_admin_can_update_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIn("success", response["data"]["updatePromotion"])
        self.assertNotIn('errors', response)

    def test_only_admin_manager_can_update_promotion(self):
        self.business.user.add(self.user)
        response = self.query_with_token(self.access_token,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])

    def test_cannot_update_promotion_for_outlet_you_dont_belong_to(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(self.access_token_master,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'You don\'t belong to outlet with this promomtion.')

    def test_cannot_update_promotion_that_doesnt_exist(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion('agfgadg',
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'Promotion with id agfgadg does not exist.')

    def test_cannot_update_promotion_with_empty_title(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion(self.promotion.id,
                                                          ''))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'title is required.')

    def test_cannot_update_promotion_with_existing_title(self):
        response = self.query_with_token(
            self.access_token_master, update_promotion(
                self.second_promotion.id, self.promotion.title))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'Promotion with title my promo already exists.')

    def test_cannot_update_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
