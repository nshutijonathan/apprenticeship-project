from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (order, approve_supplier_order,
                                                 edit_order,
                                                 send_supplier_order_emails,
                                                 mark_supplier_order_as_sent)

from healthid.apps.orders.models.orders import SupplierOrderDetails


class TestOrders(BaseConfiguration):
    '''Class to test orders operations
    '''

    def test_initiate_order(self):
        '''Method to test that users can be able to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, order.format(outlet_id=self.outlet.id))
        self.assertNotIn('errors', response)

    def test_admin_approve_supplier_orders(self):
        """Test an admin can approve orders"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        supplier_order_ids = """["{}", "{}"]""".format(id1, id2)
        response = self.query_with_token(
            self.access_token_master,
            approve_supplier_order.format(
                order_id=self.order.id,
                additional_notes=" ",
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)

    def test_edit_initiated_order(self):
        '''Method to test that users can be edit to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, edit_order.format(outlet_id=self.outlet.id,
                                                 order_id=self.order.id))
        self.assertNotIn('errors', response)

    def test_admin_approve_supplier_orders_with_invalid_ids(self):
        """Test an admin can approve orders"""
        supplier_order_ids = ["1233", "q3q4234"]
        response = self.query_with_token(
            self.access_token_master,
            approve_supplier_order.format(
                order_id=self.order.id,
                additional_notes=" ",
                supplier_order_ids=supplier_order_ids))
        self.assertIn('errors', response)

    def test_admin_supplier_orders_emails(self):
        """Test an admin can send supplier order emails"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        supplier_order_ids = """["{}", "{}"]""".format(id1, id2)
        response = self.query_with_token(
            self.access_token_master,
            send_supplier_order_emails.format(
                order_id=self.order.id,
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)

    def test_marking_supplier_orders_as_sent(self):
        """Test an admin can send supplier order emails"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        )

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        )

        supplier_order_ids = """["{}", "{}"]""".format(id1.id, id2.id)
        response = self.query_with_token(
            self.access_token_master,
            mark_supplier_order_as_sent.format(
                order_id=self.order.id,
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)
