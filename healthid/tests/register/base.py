from healthid.tests.base_config import BaseConfiguration
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.register.models import Register


class RegisterBaseCase(BaseConfiguration):
    def create_receipt_template(self):
        outlet = self.outlet
        return ReceiptTemplate.objects.create(
            cashier=False, discount_total=False, outlet_id=outlet.id,
            total_tax=True, subtotal=True, purchase_total=True,
            change_due=False, loyalty=True, amount_to_pay=False, receipt=False,
            receipt_no=True)

    def create_register(self):
        receipt_template = self.create_receipt_template()
        return Register.objects.create(
            name="liver moore",
            outlet_id=receipt_template.outlet_id,
            receipt_id=receipt_template.id)
