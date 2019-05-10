from healthid.tests.test_fixtures.sales import delete_promotion
from healthid.tests.sales.promotion_base import TestPromotion


class TestDeletePromotion(TestPromotion):
    def test_admin_can_delete_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         delete_promotion(self.promotion.id))
        self.assertIn("success", response["data"]["deletePromotion"])
        self.assertNotIn('errors', response)

    def test_cannot_delete_promotion_for_outlet_you_dont_belong_to(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(self.access_token_master,
                                         delete_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'You don\'t belong to outlet with this promomtion.')

    def test_cannot_delete_promotion_that_doesnt_exist(self):
        promotion_id = self.promotion.id
        self.query_with_token(self.access_token_master,
                              delete_promotion(promotion_id))
        response = self.query_with_token(self.access_token_master,
                                         delete_promotion(promotion_id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         f'Promotion with id {promotion_id} does not exist.')

    def test_cannot_delete_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         delete_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
