from healthid.tests.receipts.base import ReceiptBaseCase
from healthid.apps.receipts.models import FieldSet
from healthid.tests.test_fixtures.fieldset import (
    create_fieldset, update_fieldset, delete_fieldset)


class FieldSetTestCase(ReceiptBaseCase):

    def test_create_fieldset(self):
        receipt_template = self.create_receipt_template()
        response = self.query_with_token(
            self.access_token_master,
            create_fieldset(receipt_template.id),
        )
        self.assertResponseNoErrors(
            response, {"createFieldSet": {
                'fieldSet': {'cashier': "Cashier is"}
            }})

    def test_update_fieldset(self):
        fieldset = self.create_fieldset()
        response = self.query_with_token(
            self.access_token_master,
            update_fieldset(fieldset.id),
        )
        self.assertResponseNoErrors(
            response, {"updateFieldSet": {
                'fieldSet': {
                    'id': fieldset.id, 'cashier': "No cashier",
                }
            }})

    def test_fieldset_model(self):
        field_set = self.create_fieldset()
        all_fieldsets = FieldSet.objects.all()
        self.assertQuerysetEqual(
            all_fieldsets, [f'<FieldSet: {field_set.id}>'])

    def test_delete_fieldset(self):
        fieldset = self.create_fieldset()
        response = self.query_with_token(
            self.access_token_master,
            delete_fieldset(fieldset.id))
        self.assertIn("success", response["data"]["deleteFieldSet"])
