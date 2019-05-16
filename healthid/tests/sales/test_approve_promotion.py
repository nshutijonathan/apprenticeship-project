from healthid.tests.test_fixtures.sales import approve_promotion
from healthid.tests.sales.promotion_base import TestPromotion


class TestApprovePromotion(TestPromotion):
    def setUp(self):
        super().setUp()
        self.promotion.is_approved = False
        self.promotion.save()

    def test_admin_can_approve_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         approve_promotion(self.promotion.id))
        self.assertIn("success", response["data"]["approvePromotion"])
        self.assertNotIn('errors', response)

    def test_cannot_approve_promotion_for_outlet_you_dont_belong_to(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(self.access_token_master,
                                         approve_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'You don\'t belong to outlet with this promomtion.')

    def test_cannot_approve_promotion_that_doesnt_exist(self):
        response = self.query_with_token(self.access_token_master,
                                         approve_promotion('iewi1237011'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         f'Promotion with id iewi1237011 does not exist.')

    def test_cannot_approve_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         approve_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
