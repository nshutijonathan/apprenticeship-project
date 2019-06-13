from healthid.tests.base_config import BaseConfiguration
from healthid.apps.orders.models.orders import Order, OrderDetails
from healthid.utils.orders_utils.supplier_order_details import \
    create_suppliers_order_details
from healthid.tests.test_fixtures.orders import \
    suppliers_order_details, supplier_order_details


class TestSupplierOrderDetails(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.order = self.create_order()
        self.order_details = self.create_order_details(self.order)
        self.suppliers_order_details = \
            create_suppliers_order_details(self.order)

    def create_order(self):
        order = Order(name='order',
                      delivery_date='2019-10-05',
                      destination_outlet=self.outlet)
        order.save()
        return order

    def create_order_details(self, order):
        return OrderDetails.objects.create(product=self.product, quantity=5,
                                           supplier=self.supplier, order=order)

    def test_create_supplier_order_details_function(self):
        self.assertEqual(len(self.suppliers_order_details), 1)

    def test_user_can_retrieve_suppliers_order_details_for_order(self):
        response = self.query_with_token(
            self.access_token,
            suppliers_order_details.format(order_id=self.order.id)
        )
        self.assertIsNotNone(response['data']['suppliersOrderDetails'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_supplier_order_details_for_order(self):
        response = self.query_with_token(
            self.access_token,
            supplier_order_details.format(
                order_id=self.order.id, supplier_id=self.supplier.id)
        )
        self.assertIsNotNone(response['data']['supplierOrderDetails'])
        self.assertNotIn('errors', response)
