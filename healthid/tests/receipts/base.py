from healthid.tests.outlets.base import OutletBaseTest
from healthid.apps.receipts.models import ReceiptTemplate, FieldSet


class ReceiptBaseCase(OutletBaseTest):
    def create_receipt_template(self):
        outlet = self.create_outlet()
        return ReceiptTemplate.objects.create(
            cashier=False, discount_total=False, outlet_id=outlet.id,
            total_tax=True, subtotal=True, purchase_total=True,
            change_due=False, loyalty=True, amount_to_pay=False, receipt=False,
            receipt_no=True)

    def create_fieldset(self):
        receipt_template = self.create_receipt_template()
        return FieldSet.objects.create(
            cashier="Cashier is", discount_total="Discounted by",
            total_tax="A tax of", subtotal="subtotal of",
            purchase_total="total", change_due="your change",
            loyalty="loyalty yes", loyalty_earned="new points",
            loyalty_balance="total points", amount_to_pay="pay",
            receipt="your receipt", receipt_no="no",
            footer="Thanks for coming",
            receipt_template_id=receipt_template.id,
        )
