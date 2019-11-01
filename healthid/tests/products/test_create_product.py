from django.core.management import call_command

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import (
    approve_proposed_edits, approved_product_query, backup_supplier,
    create_product, create_product_2, decline_proposed_edits, delete_product,
    product_query, proposed_edits_query, proposed_product_query,
    near_expired_product_query, supplier_mutation,
    update_a_product_loyalty_weight, update_loyalty_weight,
    update_product, create_new_product)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import \
    PRODUCTS_SUCCESS_RESPONSES


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
        self.product = create_product_2(
            self.supplier_id, self.backup_id, self.user, self.outlet)
        self.product_2 = create_new_product(
            name="Cod Liver Oil",
            description="Fish oil",
            brand="Seaman's",
            manufacturer="GSK",
            category=self.product_category,
            supplier_id=self.supplier_id,
            backup_id=self.backup_id,
            user=self.user,
            outlet=self.outlet
        )
        self.product_3 = create_new_product(
            name="Lozenge",
            description="Sore throat relief",
            brand="Mazeltov",
            manufacturer="J&J",
            category=self.product_category,
            supplier_id=self.supplier_id,
            backup_id=self.backup_id,
            user=self.user,
            outlet=self.outlet
        )

    def test_create_product(self):
        """method for creating a product"""
        response = self.query_with_token(
            self.access_token,
            create_product.format(
                supplier_id=self.supplier_id, backup_id=self.backup_id))
        self.assertIn('data', response)

    def test_already_existing_product_name(self):
        """method tests for an already existing product name """
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
        response = self.query_with_token(
            self.access_token, product_query)
        self.assertIn('products', response['data'])

    def test_proposed_edits_query(self):
        response = self.query_with_token(
            self.access_token, proposed_edits_query)
        self.assertIn('proposedEdits', response['data'])

    def test_proposed_product_query(self):
        response = self.query_with_token(
            self.access_token, proposed_product_query)
        self.assertIn('proposedProducts', response['data'])

    def test_approved_product_query(self):
        response = self.query_with_token(
            self.access_token, approved_product_query)
        self.assertIn('approvedProducts', response['data'])

    def test_update_product(self):
        update_name = 'Cold cap'
        response = self.query_with_token(
            self.access_token, update_product(self.product.id, update_name))
        product_name = response['data']['updateProduct']['product']
        self.assertIn(update_name, product_name['productName'])

    def test_update_loyalty_weight(self):
        """Test method for updating loyalty weight"""
        data = {
            "product_category": self.product.product_category.id,
            "loyalty_value": 10
        }
        response = self.query_with_token(self.access_token_master,
                                         update_loyalty_weight.format(**data))
        self.assertIn("data", response)
        self.assertNotIn("errors", response)

    def test_update_loyalty_weight_with_invalid_value(self):
        """Try to update loyalty weight with a less than one value"""
        data = {
            "product_category": self.product.product_category.id,
            "loyalty_value": -1
        }
        response = self.query_with_token(self.access_token_master,
                                         update_loyalty_weight.format(**data))
        self.assertIn("errors", response)

    def test_update_a_product_loyalty_weight(self):
        """Test method for updating a product loyalty weight"""
        data = {"product_id": self.product.id, "loyalty_value": 10}
        response = self.query_with_token(
            self.access_token_master,
            update_a_product_loyalty_weight.format(**data))
        self.assertIn("data", response)
        self.assertNotIn("errors", response)

    def test_update_a_product_loyalty_weight_with_invalid_value(self):
        """Try to update loyalty weight with a less than one value"""
        data = {"product_id": self.product.id, "loyalty_value": -1}
        response = self.query_with_token(
            self.access_token_master,
            update_a_product_loyalty_weight.format(**data))
        self.assertIn("errors", response)

    def test_update_approved_product(self):
        update_name = 'Cold cap'
        message = PRODUCTS_SUCCESS_RESPONSES["approval_pending"]
        response = self.query_with_token(
            self.access_token, update_product(self.product.id, update_name))
        self.assertIn(message, response['data']['updateProduct']['message'])
        self.assertNotEqual(
            str(self.product.id),
            response['data']['updateProduct']['product']['id'])

    def test_delete_approved_product(self):
        response = self.query_with_token(self.access_token,
                                         delete_product(self.product.id))
        self.assertEqual("Approved product can't be deleted.",
                         response["errors"][0]["message"])

    def test_delete_proposed_product(self):
        self.product.is_approved = False
        self.product.save()
        response = self.query_with_token(self.access_token,
                                         delete_product(self.product.id))
        self.assertIn("success", response["data"]["deleteProduct"])

    def test_approve_edit_request(self):
        update_name = 'Cold cap'
        edit_request = self.query_with_token(
            self.access_token, update_product(self.product.id, update_name))
        edit_request_id = edit_request['data']['updateProduct']['product'][
            'id']
        response = self.query_with_token(
            self.access_token_master,
            approve_proposed_edits.format(
                product_id=self.product.id, edit_request_id=edit_request_id))
        self.assertIn(SUCCESS_RESPONSES[
            "approval_success"].format(
            "Edit request"), response['data'][
            'approveProposedEdits']['message'])
        self.assertIn('data', response)

    def test_decline_edit_request(self):
        update_name = 'Cold cap'
        edit_request = self.query_with_token(
            self.access_token, update_product(self.product.id, update_name))
        edit_request_id = edit_request['data']['updateProduct']['product'][
            'id']
        response = self.query_with_token(
            self.access_token_master,
            decline_proposed_edits.format(
                product_id=self.product.id, edit_request_id=edit_request_id))
        self.assertIn(PRODUCTS_SUCCESS_RESPONSES[
                          "edit_request_decline"].format("Cold cap"),
                      response['data']['declineProposedEdits']['message'])

    def test_near_expire_product_query(self):
        response = self.query_with_token(
            self.access_token, near_expired_product_query)
        self.assertIn('nearExpiredProducts', response['data'])
