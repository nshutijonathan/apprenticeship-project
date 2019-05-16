from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import (
    retrieve_promotions, retrieve_promotion_types,
    retrieve_promotions_pending_approval
)


class TestRetrievePromotion(TestPromotion):
    def test_user_can_retrieve_outlet_promotions(self):
        response = self.query_with_token(self.access_token_master,
                                         retrieve_promotions(self.outlet.id))
        self.assertEqual(response['data']['outletPromotions'][0]['id'],
                         str(self.promotion.id))

    def test_cannot_retrieve_promotion_for_outlet_you_dont_belong_to(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(self.access_token_master,
                                         retrieve_promotions(self.outlet.id))
        self.assertIsNotNone(response['errors'])

    def test_cannot_retrieve_outlet_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         retrieve_promotions(self.outlet.id))
        self.assertIsNotNone(response['errors'])

    def test_user_can_retrieve_promotion_types(self):
        response = self.query_with_token(self.access_token_master,
                                         retrieve_promotion_types())
        self.assertEqual(response['data']['promotionTypes'][0]['id'],
                         str(self.promotion_type.id))

    def test_admin_can_retrieve_outlet_promotions_pending_approval(self):
        self.promotion.is_approved = False
        self.promotion.save()
        response = self.query_with_token(
            self.access_token_master,
            retrieve_promotions_pending_approval(self.outlet.id)
        )
        self.assertEqual(
            response['data']['promotionsPendingApproval'][0]['id'],
            str(self.promotion.id)
        )

    def test_cant_retrieve_unapproved_promotion_for_outlet_dont_belong(self):
        self.outlet.user.remove(self.master_admin_user)
        response = self.query_with_token(
            self.access_token_master,
            retrieve_promotions_pending_approval(self.outlet.id)
        )
        self.assertIsNotNone(response['errors'])

    def test_cant_retrieve_outlet_unapproved_promotion_unauthenticated(self):
        response = self.query_with_token(
            '', retrieve_promotions_pending_approval(self.outlet.id)
        )
        self.assertIsNotNone(response['errors'])
